from pandas_datareader import data
from datetime import datetime, timedelta
from bokeh.plotting import figure, show, output_file
from bokeh.models.tools import HoverTool
from bokeh.models.sources import ColumnDataSource
import sys

# taking input from command line
arg_input = sys.argv[1:]


def stock_data(ticks, starts, ends):
    """Creating a dataframe based on stock name, start date, and end date

    Args:
        ticks (str): stock name in ticks (ex: Google: GOOG)
        starts (datetime obj): starting date for the chart
        ends (datetime obj): end date for the chart

    Returns:
        dataframe: fetched pandas dataframe for the stock
    """           
    
    stock_data_frame= data.DataReader(name= ticks, data_source= "stooq", start= starts, end= ends)
    print("Stock name found! Fetching...")
    return stock_data_frame


def bull_bear(c, o):
    """Function to distinguish between bullish bar and bearish bar

    Args:
        c (DataFrame obj): data for the close price
        o (DataFrame obj): data for the open price

    Returns:
        str: status for the data based on open and close price
    """    
    if c > o:
        value= "Bullish"
    elif c < o:
        value= "Bearish"
    else:
        value= "Equal"
    return value


def main_program():
    """
    Main program to plot the chart
    """  
    # fetching global variable from sys arg  
    global arg_input
    stock_name = arg_input[0].upper()
    if len(arg_input) > 1:
        syear, smonth, sday = arg_input[1].split('-')
        eyear, emonth, eday = arg_input[2].split('-')
            
        start_date = datetime(int(syear), int(smonth), int(sday))
        end_date = datetime(int(eyear), int(emonth), int(eday))
    else:
        start_date = datetime.now() - timedelta(days= 30)
        end_date = datetime.now()
    
    #using try and except to handle errors
    try:
        df = stock_data(stock_name, start_date, end_date)

        df["Status"]= [bull_bear(c, o) for c, o in zip(df.Close, df.Open)]
        df["Median"]= (df.Open + df.Close)/2
        df["Height"]= abs(df.Open - df.Close)
        df['index']= df.index
        
        # creating a ColumnDataSource object to made plotting easier
        cds = ColumnDataSource(df)        

        # plot figure config
        plot= figure(x_axis_type= "datetime", width= 1000, height= 300, sizing_mode= "scale_width")
        plot.title.text= stock_name + " Candlestick Chart " + "(" + start_date.strftime('%d/%m/%Y') + " - " + end_date.strftime('%d/%m/%Y') + ")"
        plot.grid.grid_line_alpha = 0

        hours_12= 12*60*60*1000
        
        # adding hovertool for price
        hover = HoverTool(tooltips= [('High', '@High'), ('Low', '@Low'),
                                        ('Open', '@Open'), ('Close', '@Close')], mode= 'vline')
        plot.add_tools(hover)

        # plot the chart
        plot.segment('index', 'High', 'index', 'Low', color= "Black", source= cds)

        plot.rect(df.index[df.Status == "Bullish"], df.Median[df.Status == "Bullish"], 
                hours_12, df.Height[df.Status == "Bullish"], fill_color= "green", line_color= "black")
        plot.rect(df.index[df.Status == "Bearish"], df.Median[df.Status == "Bearish"], 
                hours_12, df.Height[df.Status == "Bearish"], fill_color= "#FF3333", line_color= "black")
        
        # creating an output file based on the chart name   
        output_file(f"{stock_name}_dailychart.html")
        show(plot)
    
    except:
        print('Something wrong with your arguments, try again.')

# initialize the program
if __name__ == ('__main__') and len(arg_input) != 0:
    main_program()
else:
    print(doc_help())