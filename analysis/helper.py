""" Helper functions for data analysis """

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# DF Manipulation

def add_time_col(df):
    n_rows = df.shape[0] # get number of rows
    df.insert(0, 'Timestep', pd.Series(range(n_rows))) # insert new column at index 0
    return df

def split_column_values(df, col_name):
    """
    Splits the values in a column by commas and creates a new column for each value.

    Args:
        df (pandas.DataFrame): A pandas DataFrame.
        col_name (str): The name of the column to split.

    Returns:
        A pandas DataFrame with additional columns for each value in the input column.
    """
    # Get the unique values in the column
    unique_values = set(df[col_name].str.cat(sep=',').split(','))

    # Create a new column for each unique value
    for value in unique_values:
        df[value] = df[col_name].str.contains(value).astype(int)

    # Drop the original column
    df.drop(col_name, axis=1, inplace=True)

    return df


def unpack_and_join(df, column_name):
    """
    Unpacks the values in a column by commas and creates a new column for each value. Removes square brackets from the values.

    Args:
        df (pandas.DataFrame): A pandas DataFrame.
        column_name (str): The name of the column to unpack.

    Returns:
        A pandas DataFrame with additional columns for each value in the input column.
        
    """
    # Get the column values as a list of strings
    column_values = df[column_name].tolist()

    # Strip the square brackets from the strings
    column_values = [s.strip("[]") for s in column_values]

    # Split the strings on commas and create a list of lists
    split_values = [s.split(",") for s in column_values]

    # Get the number of columns needed
    num_cols = max([len(row) for row in split_values])

    # Create the new columns in the output dataframe
    column_names = [column_name+"_unpacked_"+str(i) for i in range(num_cols)]
    new_df = pd.DataFrame(columns=column_names)

    # Loop over the original column values and add the unpacked values to the new dataframe
    for vals in split_values:
        row_data = {}
        for i in range(num_cols):
            if i < len(vals):
                row_data[column_name+"_unpacked_"+str(i)] = vals[i].strip()
            else:
                row_data[column_name+"_unpacked_"+str(i)] = ""
            frow = pd.DataFrame(row_data, index=[i])
        # full_row_data = pd.concat([df, df_newrow])

        new_df = new_df.append(row_data, ignore_index=True)

    # Merge the original dataframe with the new unpacked dataframe
    merged_df = pd.concat([df, new_df], axis=1)

    return merged_df


# Plotting


def plot_data_scatter(df, x_col, y_col):
    """
    Plots data from two columns in a Pandas DataFrame using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.
    x_col : str
        The name of the column containing the x-axis data.
    y_col : str
        The name of the column containing the y-axis data.

    Returns:
    --------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure object containing the scatter plot.
    """
    fig = px.scatter(df, x=x_col, y=y_col)
    return fig

def plot_data_line(df, x_col, y_col):
    """
    Plots data from two columns in a Pandas DataFrame using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.
    x_col : str
        The name of the column containing the x-axis data.
    y_col : str
        The name of the column containing the y-axis data.

    Returns:
    --------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure object containing the line plot.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines'))
    fig.update_layout(title='Line Plot', xaxis_title=x_col, yaxis_title=y_col)
    return fig

def plot_data_heatmap(df, x_col, y_col, z_col):
    """
    Plots data from three columns in a Pandas DataFrame using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.
    x_col : str
        The name of the column containing the x-axis data.
    y_col : str
        The name of the column containing the y-axis data.
    z_col : str
        The name of the column containing the z-axis data.

    Returns:
    --------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure object containing the heatmap.
    """
    fig = go.Figure()
    fig.add_trace(go.Heatmap(x=df[x_col], y=df[y_col], z=df[z_col]))
    fig.update_layout(title='Heatmap', xaxis_title=x_col, yaxis_title=y_col)
    return fig

def plot_data_lines(df, x_col, y_cols):
    """
    Plots data from multiple columns in a Pandas DataFrame as multiple lines using Plotly.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.
    x_col : str
        The name of the column containing the x-axis data.
    y_cols : list of str
        The names of the columns containing the y-axis data.

    Returns:
    --------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure object containing the multiple line plot.
    """
    fig = go.Figure()
    for y_col in y_cols:
        fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines', name=y_col))

    fig.update_layout(title='Multiple Line Plot', xaxis_title=x_col, yaxis_title='Value')
    
    # Sort the y-axis in ascending order
    fig.update_yaxes(autorange="reversed")
    
    return fig
