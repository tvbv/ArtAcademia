#Report of Learning Session
#1 - Visualisation of learning confidence over time
import json
import os
import matplotlib.pyplot as plt

# Define the absolute path to the JSON input file
filepath = "/Users/glencarter/Desktop/PhD/Thesis/Scripts/Mistral/input.json"

def read_json(file_path):
    """Read JSON file and return the data."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def aggregate_confidence_scores(file_path):
    """Aggregate confidence scores from a specific JSON file."""
    confidence_scores = []
    feedbacks = []
    follow_up_questions = []

    data = read_json(file_path)
    for entry in data:
        confidence_scores.append(entry['confidence'])
        feedbacks.append(entry['feedback'])
        follow_up_questions.append(entry['follow_up_question'])
    
    aggregated_data = {
        "confidence_scores": confidence_scores,
        "feedbacks": feedbacks,
        "follow_up_questions": follow_up_questions
    }
    
    return aggregated_data

def generate_report(data):
    """Generate a report based on the aggregated data."""
    report = []
    report.append("User Learning Report")
    report.append("=" * 20)
    
    report.append(f"Confidence Scores: {data['confidence_scores']}")
    report.append(f"Average Confidence Score: {sum(data['confidence_scores']) / len(data['confidence_scores']):.2f}")
    
    report.append("Feedbacks:")
    for feedback in data['feedbacks']:
        report.append(f"  - {feedback}")
    
    report.append("Follow-up Questions:")
    for question in data['follow_up_questions']:
        report.append(f"  - {question}")
    
    return "\n".join(report)

def save_report(report, output_path):
    """Save the report to a specified file."""
    with open(output_path, 'w') as file:
        file.write(report)

def plot_confidence_scores(confidence_scores, output_path):
    """Plot the confidence scores and save the plot."""
    plt.figure(figsize=(10, 6))  # Standardize the plot to be square
    plt.plot(confidence_scores, marker='o', linestyle='-', color='b')
    plt.xlabel('Sessions', fontsize=12)
    plt.ylabel('Confidence Score', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

def main():
    # Use the absolute path to the input JSON file
    input_file = filepath  # Path to the specific input JSON file
    output_report_file = '/Users/glencarter/Desktop/PhD/Thesis/Scripts/Mistral/learning_report.txt'  # Path to the output report file
    output_plot_file = '/Users/glencarter/Desktop/PhD/Thesis/Scripts/Mistral/confidence_scores_plot.png'  # Path to the output plot file

    # Aggregate confidence scores and other data
    aggregated_data = aggregate_confidence_scores(input_file)

    # Generate report
    report = generate_report(aggregated_data)

    # Save report to a file
    save_report(report, output_report_file)
    print(f"Report saved to {output_report_file}")

    # Plot confidence scores and save the plot
    plot_confidence_scores(aggregated_data['confidence_scores'], output_plot_file)
    print(f"Confidence scores plot saved to {output_plot_file}")

if __name__ == "__main__":
    main()


def provide_personalized_content(confidence_scores, feedbacks, follow_up_questions):
    low_confidence_indices = [i for i, score in enumerate(confidence_scores) if score < 3]
    high_confidence_indices = [i for i, score in enumerate(confidence_scores) if score >= 3]
    
    personalized_content = {
        "improvement_areas": [follow_up_questions[i] for i in low_confidence_indices],
        "strength_areas": [follow_up_questions[i] for i in high_confidence_indices]
    }
    
    return personalized_content

def main():
    input_file = filepath  # Path to the specific input JSON file
    output_report_file = '/Users/glencarter/Desktop/PhD/Thesis/Scripts/Mistral/learning_report.txt'  # Path to the output report file
    output_plot_file = '/Users/glencarter/Desktop/PhD/Thesis/Scripts/Mistral/confidence_scores_plot.png'  # Path to the output plot file

    # Aggregate confidence scores and other data
    aggregated_data = aggregate_confidence_scores(input_file)

    # Generate report
    report = generate_report(aggregated_data)

    # Save report to a file
    save_report(report, output_report_file)
    print(f"Report saved to {output_report_file}")

    # Plot confidence scores and save the plot
    plot_confidence_scores(aggregated_data['confidence_scores'], output_plot_file)
    print(f"Confidence scores plot saved to {output_plot_file}")
    
    # Provide personalized content
    personalized_content = provide_personalized_content(aggregated_data['confidence_scores'], aggregated_data['feedbacks'], aggregated_data['follow_up_questions'])
    print("Personalized Content for Improvement:")
    print(personalized_content["improvement_areas"])
    print("Areas of Strength:")
    print(personalized_content["strength_areas"])

if __name__ == "__main__":
    main()
