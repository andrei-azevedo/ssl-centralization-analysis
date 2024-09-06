import matplotlib.pyplot as plt

def plot_performance():
    # Data
    solutions = ['Single Thread', 'Two Threads', 'Multithread']
    times = [6.9 * 60, 3.2 * 60, 5]  # Convert hours to minutes for consistency

    # Plot
    plt.figure(figsize=(10, 6))
    # Shades of gray for the bars
    colors = ['#707070', '#a0a0a0', '#d0d0d0']
    plt.barh(solutions, times, color=colors)
    
    # Adding text annotation
    total_domains = 5000
    plt.text(0.95, 0.5, f'Total domains: {total_domains}', 
             horizontalalignment='right', 
             verticalalignment='top',              
             transform=plt.gca().transAxes, 
             fontsize=10, 
             bbox=dict(facecolor='white', alpha=0.5))
    
    plt.xlabel('Time (minutes)')
    plt.title('Performance Comparison of Solutions')
    plt.gca().invert_yaxis()  # To have the highest bar at the top
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.show()

# Call the function to display the plot
plot_performance()