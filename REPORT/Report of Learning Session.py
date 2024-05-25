#Report of Learning Session
#1 - Visualisation of learning confidence over time
import json
import os


def measure_accuracy(user_input, expected_output):
    """
    This function measures the accuracy of the user's input compared to the expected output.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Create a TfidfVectorizer object
    vectorizer = TfidfVectorizer()

    # Fit and transform the user input and expected output
    X = vectorizer.fit_transform([user_input, expected_output])

    # Calculate the cosine similarity between the user input and expected output
    similarity = cosine_similarity(X)

    return similarity[0][1]


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
    confidence_scores.append(data['confidence'])
    feedbacks.append(data['feedback'])
    follow_up_questions.append(data['follow_up_question'])
    
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
    
    # TODO: iterate on the user messages and bot responses (expected output)
    #  measure accuracy between user input and bot output
    # accuracy = measure_accuracy(msg_user, msg_bot_expected_output)

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

def main():
    input_file = '/mnt/data/input.json'  # Path to the specific input JSON file
    output_file = '/mnt/data/learning_report.txt'  # Path to the output report file

    # Aggregate confidence scores and other data
    aggregated_data = aggregate_confidence_scores(input_file)

    # Generate report
    report = generate_report(aggregated_data)

    # Save report to a file
    save_report(report, output_file)
    print(f"Report saved to {output_file}")

if __name__ == "__main__":
    main()
