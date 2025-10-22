#!/usr/bin/env python3
"""
CARMA Retrieval Evaluation
Measures recall@k and precision@k for fragment retrieval quality
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class RetrievalEvaluator:
    """
    Evaluates CARMA retrieval quality using a QA set
    """
    
    def __init__(self, qa_set_file: str = 'data_core/retrieval_qa/qa_set.json'):
        self.qa_set_file = Path(qa_set_file)
    
    def create_qa_set(self, questions: List[str], expected_fragments: List[Set[str]]) -> Dict[str, Any]:
        """
        Create a QA set for retrieval evaluation
        
        Args:
            questions: List of test questions
            expected_fragments: List of sets of expected fragment IDs for each question
        
        Returns:
            QA set dictionary
        """
        qa_set = {
            'created': datetime.now().isoformat(),
            'version': '1.0',
            'test_cases': []
        }
        
        for i, (question, expected) in enumerate(zip(questions, expected_fragments)):
            qa_set['test_cases'].append({
                'id': f"qa_{i+1}",
                'question': question,
                'expected_fragments': list(expected),
                'min_recall': 0.8  # At least 80% of expected fragments should be retrieved
            })
        
        # Save QA set
        self.qa_set_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.qa_set_file, 'w') as f:
            json.dump(qa_set, f, indent=2)
        
        return qa_set
    
    def evaluate_retrieval(self, k: int = 5) -> Dict[str, Any]:
        """
        Evaluate CARMA retrieval against QA set
        
        Args:
            k: Number of top results to consider
        
        Returns:
            Evaluation results with recall@k and precision@k
        """
        if not self.qa_set_file.exists():
            return {'error': 'QA set not found. Create one first with create_qa_set()'}
        
        # Load QA set
        with open(self.qa_set_file, 'r') as f:
            qa_set = json.load(f)
        
        # Import CARMA
        try:
            from carma_core.carma_core import CARMASystem
        except ImportError:
            return {'error': 'CARMA system not available'}
        
        carma = CARMASystem()
        
        print("="*70)
        print(f"RETRIEVAL EVALUATION @ k={k}")
        print("="*70)
        print(f"QA set: {len(qa_set['test_cases'])} test cases\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'k': k,
            'qa_set_file': str(self.qa_set_file),
            'test_results': [],
            'metrics': {}
        }
        
        total_recall = 0.0
        total_precision = 0.0
        total_cases = 0
        
        for test_case in qa_set['test_cases']:
            # Run query
            query_result = carma.process_query(test_case['question'])
            retrieved = query_result.get('fragments_found', [])[:k]
            expected = set(test_case['expected_fragments'])
            
            # Calculate metrics
            if expected:
                retrieved_set = set(retrieved)
                hits = retrieved_set.intersection(expected)
                
                recall = len(hits) / len(expected) if expected else 0.0
                precision = len(hits) / len(retrieved) if retrieved else 0.0
                
                total_recall += recall
                total_precision += precision
                total_cases += 1
                
                test_result = {
                    'id': test_case['id'],
                    'question': test_case['question'][:50],
                    'expected_count': len(expected),
                    'retrieved_count': len(retrieved),
                    'hits': len(hits),
                    'recall': recall,
                    'precision': precision,
                    'passed': recall >= test_case.get('min_recall', 0.8)
                }
                
                results['test_results'].append(test_result)
                
                status = "✓" if test_result['passed'] else "✗"
                print(f"{status} {test_case['id']}: R@{k}={recall:.2f}, P@{k}={precision:.2f}")
        
        # Calculate aggregate metrics
        if total_cases > 0:
            results['metrics'] = {
                'recall_at_k': total_recall / total_cases,
                'precision_at_k': total_precision / total_cases,
                'pass_rate': sum(1 for t in results['test_results'] if t['passed']) / total_cases
            }
            
            print("\n" + "="*70)
            print("AGGREGATE METRICS")
            print("="*70)
            print(f"Recall@{k}: {results['metrics']['recall_at_k']:.3f}")
            print(f"Precision@{k}: {results['metrics']['precision_at_k']:.3f}")
            print(f"Pass rate: {results['metrics']['pass_rate']:.1%}")
            print("="*70)
        
        # Save results
        output_dir = Path('data_core/retrieval_qa')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        return results


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CARMA Retrieval Evaluator')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Eval command
    eval_parser = subparsers.add_parser('eval', help='Evaluate retrieval quality')
    eval_parser.add_argument('--qa-set', default='data_core/retrieval_qa/qa_set.json',
                            help='QA set file')
    eval_parser.add_argument('--k', type=int, default=5,
                            help='Top k results to evaluate (default: 5)')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create sample QA set')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'eval':
        evaluator = RetrievalEvaluator(qa_set_file=args.qa_set)
        evaluator.evaluate_retrieval(k=args.k)
    
    elif args.command == 'create':
        # Create expanded QA set
        evaluator = RetrievalEvaluator()
        
        # Expanded QA set with more diverse questions
        sample_qa = [
            # Technical questions
            ("What is AI?", {"fragment_9e76c84a", "fragment_76f54754"}),
            ("Tell me about neural networks", {"fragment_90013071", "fragment_8a9fbb7c"}),
            ("How does machine learning work?", {"fragment_9e76c84a", "fragment_90013071"}),
            
            # Organization/conscientiousness
            ("How do I stay organized?", {"fragment_b438ce2c"}),
            ("What's the best way to plan my day?", {"fragment_b438ce2c"}),
            
            # Social/emotional
            ("How do I connect with people?", {"fragment_59c869ea"}),
            ("I feel anxious", {"fragment_0267e826"}),
            
            # General
            ("Tell me about yourself", {"fragment_762518da"}),
            ("What can you help me with?", {"fragment_76f54754"}),
            ("Hello", {"fragment_59c869ea", "fragment_762518da"}),
        ]
        
        questions = [q for q, _ in sample_qa]
        expected = [e for _, e in sample_qa]
        
        qa_set = evaluator.create_qa_set(questions, expected)
        
        print("="*70)
        print("EXPANDED QA SET CREATED")
        print("="*70)
        print(f"File: {evaluator.qa_set_file}")
        print(f"Test cases: {len(qa_set['test_cases'])}")
        print("\nCategories:")
        print(f"  Technical: 3")
        print(f"  Organization: 2")
        print(f"  Social/Emotional: 2")
        print(f"  General: 3")
        print("\nTo evaluate:")
        print(f"  py tools\\retrieval_eval.py eval --qa-set {evaluator.qa_set_file}")
        print("="*70)


if __name__ == "__main__":
    main()

