import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# xit7
def plot_actual_vs_pred(plotdat, observed='observed', predicted='target', title='No title'):
    """Plot predictions and actual values to visualize performance.

    Args:
        plotdat (Dataframe): Dataframe to plot
        observed (String): Column name for observed values
        predicted (String): Column name for predicted values
    """

    # Aggregate by week
    plotdat['datetime'] = pd.to_datetime(plotdat['datetime'])

    # Set the week as a new column
    plotdat['week'] = plotdat['datetime'].dt.to_period('W').apply(lambda r: r.start_time)

    # Aggregate data by week
    weekly_data = plotdat.query('is_consumption == 0').groupby('week').agg({
        observed: 'mean',  # Replace 'mean' with your preferred aggregation method
        predicted: 'mean'  # Replace 'mean' with your preferred aggregation method
    }).reset_index()

    # Set the figure size
    plt.figure(figsize=(12, 6))

    # Plotting the actual and predicted production aggregated by week
    plt.plot(weekly_data['week'], weekly_data[observed], color='forestgreen', label='observed')
    plt.plot(weekly_data['week'], weekly_data[predicted], color='red', linestyle='--', label='predicted')

    # Improve the layout
    plt.xticks(rotation=45)  # Rotate x-axis labels to prevent overlap
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format date labels
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())  # Use week locator for x-axis ticks

    # Customize the legend and titles
    plt.legend(loc='upper left')
    plt.title(title, fontsize=14)
    plt.xlabel('Week Starting', fontsize=12)
    plt.ylabel('Production (mean)', fontsize=12)

    # Mark the first week of January 2023
    # Mark January 1, 2023
    jan_2023 = pd.Timestamp('2023-01-01')
    plt.axvline(x=jan_2023, color='black', linestyle='--')

    # Adjust the x-axis limits to ensure no excessive white space
    plt.xlim(plotdat['datetime'].min(), plotdat['datetime'].max())

    # Add annotations for the years with arrows
    # Arrow pointing to the left for 2022
    plt.annotate('2022', xy=(jan_2023 - pd.Timedelta(days=0), 100), xytext=(-60, 0), textcoords='offset points',
                arrowprops=dict(facecolor='black', arrowstyle="<-"), color='black', horizontalalignment='right', verticalalignment='center')

    # Arrow pointing to the right for 2023
    plt.annotate('2023', xy=(jan_2023 + pd.Timedelta(days=0), 100), xytext=(60, 0), textcoords='offset points',
                arrowprops=dict(facecolor='black', arrowstyle="<-"), color='black', horizontalalignment='left', verticalalignment='center')


    # Show the plot
    plt.tight_layout()  # Adjust the layout to fit all elements
    plt.show()