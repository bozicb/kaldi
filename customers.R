library(xts)

getDailyCustomerData <- function(df) {

    new_df <- data.frame(ID=integer(),Date=as.Date(character()),Value=double())

    for(customer in sort(unique(df$ID))) {
        s <- subset(df, df$ID == customer)
        xs <- xts(s$Value, s$Date)
        xds <- apply.daily(xs,sum,na.rm=TRUE)
        dfxs <- data.frame(index(xds),coredata(xds))
        colnames(dfxs) <- c("Date","Value") 
        dfxs$ID <- rep(customer,dim(dfxs)[1])
        dfxs <- dfxs[c("ID","Date","Value")]
        new_df <- rbind(new_df,dfxs)
    }
new_df
}

