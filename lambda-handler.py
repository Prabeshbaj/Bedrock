import json
import logging
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda handler that ensures JSON-only output for follow-up questions
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract the previous message to analyze
        previous_message = event.get('requestBody', {}).get('message', '')
        logger.info(f"Message to analyze: {previous_message}")
        
        # If the input is empty or too short, use default questions
        if not previous_message or len(previous_message) < 10:
            return {
                "response": {
                    "followUpQuestions": [
                        "Could you tell me more about this topic?",
                        "What aspects of this subject interest you the most?",
                        "Would you like to explore any specific details?"
                    ]
                }
            }
            
        # Extract any JSON from the response if it exists
        json_match = re.search(r'({[\s\S]*"followUpQuestions"[\s\S]*})', previous_message)
        
        if json_match:
            try:
                # Try to parse the JSON if found
                json_str = json_match.group(1)
                parsed_json = json.loads(json_str)
                
                # If we have valid followUpQuestions in the JSON, use them
                if "followUpQuestions" in parsed_json and isinstance(parsed_json["followUpQuestions"], list):
                    questions = parsed_json["followUpQuestions"]
                    # Ensure we have 2-3 questions
                    if len(questions) >= 2:
                        # Limit to 3 questions max
                        return {
                            "response": {
                                "followUpQuestions": questions[:3]
                            }
                        }
            except:
                # If JSON parsing fails, continue to fallback
                logger.warning("Failed to parse JSON from the response")
        
        # Fallback: Try to extract questions using regex
        questions = re.findall(r'(?:^|\n)\s*(?:\d+\.\s*)?(.*?\?)', previous_message)
        
        # If we found at least 2 questions, use them
        if len(questions) >= 2:
            return {
                "response": {
                    "followUpQuestions": questions[:3]  # Limit to 3 questions
                }
            }
            
        # Final fallback: Generate generic contextual questions
        topic_words = [word for word in previous_message.split()[:10] if len(word) > 4]
        topic = " ".join(topic_words[:2]) if topic_words else "this topic"
        
        return {
            "response": {
                "followUpQuestions": [
                    f"What more can you tell me about {topic}?",
                    f"How has {topic} affected your perspective or experience?",
                    "Which aspects would you like to explore further?"
                ]
            }
        }
                
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Even on error, return properly formatted JSON
        return {
            "response": {
                "followUpQuestions": [
                    "Could you share more details on this subject?",
                    "What do you find most interesting about this?",
                    "Is there a specific aspect you'd like to discuss further?"
                ]
            }
        }