library(shiny)

ui <- fluidPage(
  titlePanel("Kaldi Coffee"),
  
  sidebarLayout(
    sidebarPanel(
      helpText("The selected variable will be used to analyse correlations for every 
                instance and generate graphs."),
      selectInput("var", label = "Choose a variable", choices = 
                    c("Customers","Products","Prices","Quantities","Deliveries")),
      selectInput("inst", label = "Choose an instance", choices = ""),
      actionButton("plot1", label = "Plot"),
      helpText("Time series decomposition for the selected variable."),
      selectInput("ts", label = "Choose TS variable", choices =
                    c("Customers","Products","Values")),
      actionButton("plot2", label = "Plot")
    ),
  
    mainPanel(plotOutput("result1"),
              plotOutput("result2"))
  )
)

server <- function(input, output, session) {
  customers <- subset(transactions,(quantity*price>100)&(quantity>3))
  observe({
    if (input$var == "Customers")
      updateSelectInput(session, "inst", choices = sort(unique(customers$customer_id)))
    else if (input$var == "Products")
      updateSelectInput(session, "inst", choices = sort(unique(customers$product_id)))
    else if (input$var == "Prices")
      updateSelectInput(session, "inst", choices = sort(unique(customers$price)))
    else if (input$var == "Quantities")
      updateSelectInput(session, "inst", choices = sort(unique(customers$quantity)))
    else if (input$var == "Deliveries")
      updateSelectInput(session, "inst", choices = sort(unique(as.Date(customers$delivered))))
  })
  observeEvent(input$plot1,{
    if (input$var == "Customers"){
      s <- subset(customers, customer_id == input$inst)
      output$result1 <- renderPlot({plot(s$delivered, s$quantity*s$price)})
    }
    else if (input$var == "Products"){
      s <- subset(customers, product_id == input$inst)
      output$result1 <- renderPlot({plot(s$delivered, s$quantity*s$price)})
    }
    else if (input$var == "Prices"){
      s <- subset(customers, price == input$inst)
      output$result1 <- renderPlot({plot(s$product_id, s$customer_id)})
    }
    else if (input$var == "Quantities"){
      s <- subset(customers, quantity == input$inst)
      output$result1 <- renderPlot({plot(s$product_id, s$customer_id)})
    }
    else if (input$var == "Deliveries"){
      s <- subset(customers, as.Date(delivered) == as.Date(input$inst))
      output$result1 <- renderPlot({plot(s$product_id, s$customer_id)})
    }
  })
  observeEvent(input$plot2,{
    if (input$ts == "Customers"){
      value_ts <- xts(customers$customer_id,customers$delivered)
      ts_values <- ts(apply.daily(value_ts,sum,na.rm=TRUE),frequency=7)
      output$result2 <- renderPlot({plot(decompose(ts_values))})
    }
    else if (input$ts == "Products"){
      value_ts <- xts(customers$product_id,customers$delivered)
      ts_values <- ts(apply.daily(value_ts,sum,na.rm=TRUE),frequency=7)
      output$result2 <- renderPlot({plot(decompose(ts_values))})
    }
    else if (input$ts == "Values"){
      value_ts <- xts(customers$price*customers$quantity,customers$delivered)
      ts_values <- ts(apply.daily(value_ts,sum,na.rm=TRUE),frequency=7)
      output$result2 <- renderPlot({plot(decompose(ts_values))})
    }
  })
}

shinyApp(ui = ui, server = server)