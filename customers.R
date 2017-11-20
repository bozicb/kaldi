library(xts)

getDailyCustomerData <- function() {

    dc <- read.csv("transactions.csv")
    df <- as.data.frame(cbind(dc[,1],as.Date(dc[,5]),dc[,3]*dc[,4]))
    names <- c("ID","Date","Value")
    names(df) <- names
    df[,2] <- as.Date(dc[,5])

    new_df <- data.frame(Date=as.Date(character()),Value=double(),
                     ID=integer())

    for(customer in sort(unique(df$ID))) {
        s <- subset(df, df$ID == customer)
        xs <- xts(s$Value, s$Date)
        xds <- apply.daily(xs,sum,na.rm=TRUE)
        dfxs <- data.frame(index(xds),coredata(xds))
        colnames(dfxs) <- c("Date","Value") 
        dfxs$ID <- rep(customer,dim(dfxs)[1])
        new_df <- rbind(new_df,dfxs)
    }
new_df
}

