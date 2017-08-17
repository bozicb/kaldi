import pandas as pd
import argparse
from elasticsearch import Elasticsearch, TransportError
import json


class CSV2JSON:
    def __init__(self):
        self.es = None
        self.fileName = None
        self.df = None
        self.index = None
        self.index_doc_type = None

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--fileName",
                            required=True,
                            help="Name of the csv file to convert to json and dump into elastic"
                            )
        parser.add_argument("--index",
                            required=True,
                            help="Name of the index to create in elastic"
                            )
        parser.add_argument("--doctype",
                            required=True,
                            help="Name of the document type to be created in the index"
                            )
        args = parser.parse_args()
        self.fileName = args.fileName
        self.index = args.index
        self.index_doc_type = args.doctype
        self.read_csv_file()
        self.set_elastic_index()
        self.dump_data_in_elastic()

    def read_csv_file(self):
        # read the csv file into a dataframe
        self.df = pd.read_csv(self.fileName)
        # modify the datetime format. Make sure that this is reflected in the elastic index definition
        self.df["delivered"] = pd.to_datetime(self.df["delivered"], errors="coerce").dt.strftime("%d-%m-%Y %H:%M:%S")
        # print("date coffee is delivered: "+self.df["delivered"])

        # print the header values
        # print("columns in the file: "+self.df.columns.values)

        # get the number of rows
        print("records in the file: " + str(len(self.df)))

    def set_elastic_index(self):
        # set up local elastic
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        index_definition = {
            "mappings": {
                "coffee_customer": {
                    "properties": {
                        "delivered": {
                            "type": "date",
                            "format": "dd-MM-yyyy HH:mm:ss"
                        },
                        "price": {
                            "type": "double"
                        },
                        "customer_id": {
                            "type": "integer"
                        },
                        "product_id": {
                            "type": "integer"
                        },
                        "quantity": {
                            "type": "integer"
                        },
                        "amount": {
                            "type": "double"
                        }
                    }
                }
            }
        }

        self.es.indices.delete(index=self.index, ignore=[400, 404])
        self.es.indices.create(index=self.index, ignore=400, body=index_definition)

    def dump_data_in_elastic(self):
        # print each row as a json object
        try:
            for i in self.df.index:
                #   print(i)
                coffee = self.df.loc[i].to_json()
               # coffee['amount']=coffee['price']*coffee['quantity']
               # print(coffee)
                cc = json.loads(coffee)
                if cc['price'] and cc['quantity']:
                    cc['amount'] = format(cc['price']*cc['quantity'], '.2f')
                else:
                    cc['amount'] = 0
                print(cc)
                self.es.index(index=self.index, doc_type=self.index_doc_type, id=i, body=cc)
        except TransportError as e:
            print(e.info)


if __name__ == '__main__':
    csv_to_json = CSV2JSON()
    csv_to_json.main()
