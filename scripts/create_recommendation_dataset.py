#!/usr/bin/env python3
"""
Create recommendation dataset from raw ReDial data.

Flattens conversations so that each recommender utterance mentioning movies
becomes a single instance with context.

Input: /home/stud/ivicak/bhome/redial-data/{train,test}_data.jsonl
Output: /home/stud/ivicak/bhome/repro/data/redial_{train,test}_rec.json

Flags:
  --fresh-only: Only include new recommendations (movies not mentioned earlier in conversation)
"""

import json
import os
import argparse
from tqdm import tqdm


def extract_recommendation_instances(conversation, fresh_only=False):
    """
    Extract recommendation instances from a conversation.
    
    Each instance is created when:
    - The recommender mentions at least one movie
    - There is previous conversation context
    
    Args:
        conversation: Raw ReDial conversation dict
        fresh_only: If True, only include movies not mentioned earlier in the conversation
    
    Returns list of instances with:
    - conversation_id
    - context: list of previous utterances
    - response: recommender's utterance
    - movies: list of movie IDs mentioned
    """
    messages = conversation['messages']
    movie_mentions = conversation.get('movieMentions', {})
    
    # Handle case where movieMentions might be a list or empty
    if not isinstance(movie_mentions, dict):
        movie_mentions = {}
    
    initiator_id = conversation['initiatorWorkerId']
    respondent_id = conversation['respondentWorkerId']
    
    instances = []
    context = []
    mentioned_movies = set()  # Track movies mentioned so far in conversation
    
    for msg in messages:
        sender_id = msg['senderWorkerId']
        is_recommender = (sender_id == respondent_id)
        text = msg['text']
        
        # Find movies mentioned in this message
        movies_in_msg = []
        for movie_id in movie_mentions.keys():
            if f'@{movie_id}' in text:
                movies_in_msg.append(movie_id)
        
        # Apply fresh-only filter if requested
        if fresh_only:
            # Only keep movies that haven't been mentioned before
            fresh_movies = [m for m in movies_in_msg if m not in mentioned_movies]
        else:
            fresh_movies = movies_in_msg
        
        # If recommender mentions movies and there's context, create instance
        if is_recommender and fresh_movies and context:
            # Get all movies mentioned in the conversation so far (including this turn)
            all_mentioned = mentioned_movies.union(movies_in_msg)
            
            instance = {
                'conversation_id': conversation['conversationId'],
                'context': context.copy(),
                'response': text,
                'all_movies': list(mentioned_movies),  # Movies mentioned before this turn
                'recommendations': fresh_movies,  # New movies recommended in this turn
                'movie_names': {mid: movie_mentions[mid] for mid in all_mentioned}  # ID -> name mapping
            }
            instances.append(instance)
        
        # Track all movies mentioned (for fresh_only filtering)
        mentioned_movies.update(movies_in_msg)
        
        # Add current message to context for next iteration
        context.append({
            'sender': 'recommender' if is_recommender else 'seeker',
            'text': text
        })
    
    return instances


def process_dataset(input_path, output_path, fresh_only=False):
    """
    Process a dataset file and extract all recommendation instances.
    
    Args:
        input_path: Path to input .jsonl file
        output_path: Path to output .json file
        fresh_only: If True, only include fresh (new) recommendations
    """
    print(f"Processing: {input_path}")
    if fresh_only:
        print("Mode: FRESH ONLY (excluding previously mentioned movies)")
    
    # Load conversations
    conversations = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            conversations.append(json.loads(line.strip()))
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Extract instances
    all_instances = []
    for conv in tqdm(conversations, desc="Extracting instances"):
        instances = extract_recommendation_instances(conv, fresh_only=fresh_only)
        all_instances.extend(instances)
    
    # Statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Total conversations: {len(conversations)}")
    print(f"Total recommendation instances: {len(all_instances)}")
    
    # Count unique movies
    all_movies = set()
    for inst in all_instances:
        all_movies.update(inst['recommendations'])
    print(f"Unique movies recommended: {len(all_movies)}")
    
    # Average recommendations per instance
    total_recs = sum(len(inst['recommendations']) for inst in all_instances)
    avg_recs = total_recs / len(all_instances) if all_instances else 0
    print(f"Average recommendations per instance: {avg_recs:.2f}")
    
    # Average context movies per instance
    total_context_movies = sum(len(inst['all_movies']) for inst in all_instances)
    avg_context_movies = total_context_movies / len(all_instances) if all_instances else 0
    print(f"Average context movies per instance: {avg_context_movies:.2f}")
    
    # Average context length
    avg_context = sum(len(inst['context']) for inst in all_instances) / len(all_instances) if all_instances else 0
    print(f"Average context length: {avg_context:.2f} utterances")
    print("="*60)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_instances, f, indent=2)
    
    print(f"\nSaved to: {output_path}")
    
    return all_instances


def main():
    """Process both train and test datasets."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Create recommendation dataset from raw ReDial data'
    )
    parser.add_argument(
        '--fresh-only',
        action='store_true',
        help='Only include fresh recommendations (movies not mentioned earlier in conversation)'
    )
    args = parser.parse_args()
    
    base_input = "/home/stud/ivicak/bhome/redial-data"
    base_output = "/home/stud/ivicak/bhome/repro/data"
    
    # Adjust output filenames based on mode
    suffix = '_fresh' if args.fresh_only else ''
    datasets = [
        ('train', 'train_data.jsonl', f'redial_train_rec{suffix}.json'),
        ('test', 'test_data.jsonl', f'redial_test_rec{suffix}.json')
    ]
    
    results = {}
    
    for name, input_file, output_file in datasets:
        input_path = os.path.join(base_input, input_file)
        output_path = os.path.join(base_output, output_file)
        
        if not os.path.exists(input_path):
            print(f"⚠️  Skipping {name}: {input_path} not found")
            continue
        
        print("\n" + "="*60)
        print(f"PROCESSING {name.upper()} DATASET")
        print("="*60)
        
        instances = process_dataset(input_path, output_path, fresh_only=args.fresh_only)
        results[name] = len(instances)
        print()
    
    # Prepare summary for both console and file output
    summary_lines = []
    summary_lines.append("="*60)
    summary_lines.append("SUMMARY")
    summary_lines.append("="*60)
    for name, count in results.items():
        summary_lines.append(f"{name.capitalize()}: {count} instances")
    
    # Print to console
    print("\n" + "\n".join(summary_lines))
    
    # Add total recommendations count
    if results:
        print("\nTotal recommendations:")
        
        all_datasets = {}
        total_instances = 0
        total_recommendations = 0
        total_all_mentions = 0
        all_unique_movies = set()
        all_unique_mentions = set()
        all_conversations = set()
        
        for name, _ in results.items():
            # Load the file to count recommendations
            suffix = '_fresh' if args.fresh_only else ''
            output_file = f'redial_{name}_rec{suffix}.json'
            output_path = os.path.join(base_output, output_file)
            
            with open(output_path, 'r') as f:
                instances = json.load(f)
            
            all_datasets[name] = instances
            
            total_recs = sum(len(inst['recommendations']) for inst in instances)
            unique_recs = len(set(mid for inst in instances for mid in inst['recommendations']))
            
            # Count all movie mentions per conversation (not per instance)
            conv_mentions = {}
            for inst in instances:
                conv_id = inst['conversation_id']
                if conv_id not in conv_mentions:
                    conv_mentions[conv_id] = set()
                conv_mentions[conv_id].update(inst['all_movies'])
                conv_mentions[conv_id].update(inst['recommendations'])
            
            total_mentions = sum(len(movies) for movies in conv_mentions.values())
            unique_mentions = len(set(
                mid for inst in instances 
                for mid in (inst['all_movies'] + inst['recommendations'])
            ))
            
            summary_line = f"  {name.capitalize()}: {total_recs} recommendations ({unique_recs} unique), {total_mentions} movie mentions ({unique_mentions} unique movies)"
            print(summary_line)
            summary_lines.append(summary_line)
            
            # Accumulate for combined stats
            total_instances += len(instances)
            total_recommendations += total_recs
            total_all_mentions += total_mentions
            all_conversations.update(conv_mentions.keys())
            all_unique_movies.update(mid for inst in instances for mid in inst['recommendations'])
            all_unique_mentions.update(
                mid for inst in instances 
                for mid in (inst['all_movies'] + inst['recommendations'])
            )
        
        # Combined statistics
        if len(all_datasets) > 1:
            combined_lines = [
                "\n  Combined (train+test):",
                f"    Conversations: {len(all_conversations)}",
                f"    Instances: {total_instances}",
                f"    Recommendations: {total_recommendations} total, {len(all_unique_movies)} unique",
                f"    Movie mentions: {total_all_mentions} total, {len(all_unique_mentions)} unique movies"
            ]
            for line in combined_lines:
                print(line)
                summary_lines.append(line)
    
    summary_lines.append("="*60)
    print("="*60)
    
    # Save summary to file
    suffix = '_fresh' if args.fresh_only else ''
    summary_path = os.path.join(base_output, f'dataset_statistics{suffix}.txt')
    with open(summary_path, 'w') as f:
        f.write("\n".join(summary_lines))
    
    print(f"\n📊 Statistics saved to: {summary_path}")
    print("="*60)


if __name__ == "__main__":
    main()
