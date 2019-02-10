#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

# Define UI for application that draws a histogram
ui <- fluidPage(
   
   # Application title
   titlePanel("OIData"),
   mainPanel(
     dataTableOutput('mytable')
   )
  
)

# Define server logic required to draw a histogram
server <- function(input, output) {
   
  output$mytable = renderDataTable({
    read.csv('D:/code/workspace/NSEOIDownloader/temp6/merged2.csv', header=T, check.names = FALSE)
  })
}

# Run the application 
shinyApp(ui = ui, server = server)

