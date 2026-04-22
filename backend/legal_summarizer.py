"""
Legal Document Summarization Module
Automatically generate concise summaries of long legal documents and judgments.
"""

from transformers import pipeline
import torch
from typing import Optional, Dict
import warnings
warnings.filterwarnings('ignore')

class LegalSummarizer:
    """
    Generate summaries of legal documents using transformer models
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize summarization model
        
        Args:
            model_name: HuggingFace model name for summarization
        """
        print(f"🔄 Loading summarization model: {model_name}")
        
        # Check if GPU is available
        device = 0 if torch.cuda.is_available() else -1
        
        try:
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                device=device
            )
            print(f"✅ Summarization model loaded on {'GPU' if device == 0 else 'CPU'}")
        except Exception as e:
            print(f"⚠️  Error loading model: {e}")
            print("   Falling back to default model...")
            self.summarizer = pipeline("summarization", device=device)
    
    def summarize(
        self,
        text: str,
        max_length: int = 200,
        min_length: int = 50,
        do_sample: bool = False
    ) -> Dict[str, str]:
        """
        Generate summary of legal document
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            do_sample: Whether to use sampling (False = greedy)
        
        Returns:
            Dictionary with summary and metadata
        """
        if not text or len(text.strip()) < 100:
            return {
                'summary': text,
                'original_length': len(text),
                'summary_length': len(text),
                'compression_ratio': 1.0,
                'error': 'Text too short to summarize'
            }
        
        try:
            # Truncate if too long (BART max is 1024 tokens)
            max_input_length = 1024
            if len(text.split()) > max_input_length:
                text = ' '.join(text.split()[:max_input_length])
            
            # Generate summary
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample,
                truncation=True
            )
            
            summary_text = result[0]['summary_text']
            
            return {
                'summary': summary_text,
                'original_length': len(text),
                'summary_length': len(summary_text),
                'compression_ratio': round(len(summary_text) / len(text), 2),
                'error': None
            }
        
        except Exception as e:
            return {
                'summary': text[:500] + "...",
                'original_length': len(text),
                'summary_length': 500,
                'compression_ratio': 0.0,
                'error': f"Summarization failed: {str(e)}"
            }
    
    def summarize_long_document(
        self,
        text: str,
        chunk_size: int = 1000,
        final_max_length: int = 300
    ) -> Dict[str, str]:
        """
        Summarize very long documents by chunking
        
        Args:
            text: Long document text
            chunk_size: Size of each chunk (in words)
            final_max_length: Final summary length
        
        Returns:
            Dictionary with summary and metadata
        """
        words = text.split()
        
        # If document is short enough, summarize directly
        if len(words) <= 1024:
            return self.summarize(text, max_length=final_max_length)
        
        # Split into chunks
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        print(f"📄 Summarizing {len(chunks)} chunks...")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            result = self.summarize(chunk, max_length=150, min_length=30)
            if result['error'] is None:
                chunk_summaries.append(result['summary'])
            print(f"   ✓ Chunk {i+1}/{len(chunks)} summarized")
        
        # Combine chunk summaries
        combined_summary = ' '.join(chunk_summaries)
        
        # Final summarization
        if len(combined_summary.split()) > 1024:
            combined_summary = ' '.join(combined_summary.split()[:1024])
        
        final_result = self.summarize(
            combined_summary,
            max_length=final_max_length,
            min_length=100
        )
        
        return {
            **final_result,
            'num_chunks': len(chunks),
            'method': 'hierarchical'
        }
    
    def summarize_with_bullets(self, text: str, num_points: int = 5) -> Dict[str, any]:
        """
        Generate bullet-point summary
        
        Args:
            text: Input text
            num_points: Number of key points to extract
        
        Returns:
            Dictionary with bullet points
        """
        # Get standard summary
        result = self.summarize(text, max_length=300, min_length=100)
        
        if result['error']:
            return result
        
        summary = result['summary']
        
        # Split into sentences
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        
        # Take top N sentences as bullet points
        bullet_points = sentences[:num_points]
        
        return {
            'summary': result['summary'],
            'bullet_points': bullet_points,
            'num_points': len(bullet_points),
            'original_length': result['original_length'],
            'error': None
        }

# Test function
def test_summarizer():
    """Test the legal summarizer"""
    
    print("=" * 80)
    print("LEGAL SUMMARIZATION TEST")
    print("=" * 80)
    
    summarizer = LegalSummarizer()
    
    # Sample legal text
    sample_text = """
    The Supreme Court of India in the landmark case of Kesavananda Bharati v. 
    State of Kerala established the basic structure doctrine. The court held that 
    while Parliament has wide powers to amend the Constitution, it cannot alter 
    the basic structure or framework of the Constitution. This includes features 
    like supremacy of the Constitution, republican and democratic form of government, 
    secular character of the Constitution, separation of powers, and federal character 
    of the Constitution. The judgment was delivered by a 13-judge bench and remains 
    one of the most important constitutional law decisions in India. The case arose 
    from a challenge to the 24th, 25th, 26th, and 29th amendments to the Constitution. 
    The petitioner argued that these amendments violated fundamental rights and the 
    basic structure of the Constitution. The court, in a 7-6 majority decision, 
    upheld the validity of most amendments but established the principle that certain 
    basic features of the Constitution are beyond the amending power of Parliament.
    """
    
    print("\n📄 Original Text:")
    print(f"   Length: {len(sample_text)} characters")
    print(f"   Words: {len(sample_text.split())}")
    
    # Test 1: Standard summary
    print("\n🔍 Test 1: Standard Summary")
    result1 = summarizer.summarize(sample_text)
    print(f"   Summary: {result1['summary']}")
    print(f"   Compression: {result1['compression_ratio']:.1%}")
    
    # Test 2: Bullet points
    print("\n🔍 Test 2: Bullet Point Summary")
    result2 = summarizer.summarize_with_bullets(sample_text, num_points=3)
    print("   Key Points:")
    for i, point in enumerate(result2['bullet_points'], 1):
        print(f"   {i}. {point}")
    
    print("\n" + "=" * 80)
    print("✅ Summarization tests complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_summarizer()
