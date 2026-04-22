#!/usr/bin/env python3

"""
Enhanced Training Data Generator for Legal AI
Creates high-quality training examples to improve model accuracy
"""

import json
import os
from typing import List, Dict

class LegalTrainingDataGenerator:
    """Generate enhanced training data for better legal AI responses"""
    
    def __init__(self):
        self.training_examples = []
    
    def add_case_law_example(self, case_name: str, facts: str, legal_issue: str, ruling: str, citation: str):
        """Add case law training example"""
        example = {
            "input": f"Analyze the legal implications of: {facts}",
            "context": f"Case: {case_name}\nLegal Issue: {legal_issue}",
            "expected_output": f"""## Legal Analysis: {case_name}

### Key Facts
{facts}

### Legal Issue
{legal_issue}

### Court's Ruling
{ruling}

### Legal Principles Established
- The court's decision establishes important precedent
- This ruling clarifies the interpretation of relevant laws
- The decision has implications for similar future cases

### Citation
{citation}

### Practical Implications
This case affects legal practice in the following ways:
- Provides guidance for similar legal situations
- Helps lawyers advise clients on related matters
- Influences judicial decision-making in comparable cases""",
            "category": "case_law",
            "entities": self._extract_entities(f"{case_name} {facts} {legal_issue}")
        }
        self.training_examples.append(example)
    
    def add_statutory_interpretation_example(self, act_name: str, section: str, interpretation: str, application: str):
        """Add statutory interpretation training example"""
        example = {
            "input": f"Explain Section {section} of the {act_name}",
            "context": f"Statutory Interpretation Request",
            "expected_output": f"""## {act_name}: Section {section}

### Text of the Section
{section}

### Legal Interpretation
{interpretation}

### Practical Application
{application}

### Key Points
- This section establishes specific legal requirements
- Courts have interpreted this provision in the context of...
- The section applies to situations involving...

### Related Provisions
This section should be read in conjunction with:
- Other relevant sections of the same Act
- Complementary legislation
- Judicial precedents interpreting similar provisions""",
            "category": "statutory_interpretation",
            "entities": self._extract_entities(f"{act_name} {section}")
        }
        self.training_examples.append(example)
    
    def add_legal_procedure_example(self, procedure_type: str, steps: List[str], requirements: List[str], timeline: str):
        """Add legal procedure training example"""
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        req_text = "\n".join([f"• {req}" for req in requirements])
        
        example = {
            "input": f"What is the procedure for {procedure_type}?",
            "context": f"Legal Procedure Inquiry",
            "expected_output": f"""## Legal Procedure: {procedure_type}

### Required Steps
{steps_text}

### Legal Requirements
{req_text}

### Timeline
{timeline}

### Important Considerations
- Ensure all documentation is properly prepared
- Follow procedural requirements strictly
- Meet all deadlines to avoid procedural dismissal
- Consider seeking professional legal assistance

### Common Pitfalls to Avoid
- Missing filing deadlines
- Incomplete documentation
- Failure to follow proper procedure
- Ignoring jurisdictional requirements""",
            "category": "legal_procedure",
            "entities": self._extract_entities(f"{procedure_type} {' '.join(steps)}")
        }
        self.training_examples.append(example)
    
    def add_prediction_example(self, case_description: str, prediction: str, confidence: float, factors: List[str]):
        """Add case outcome prediction training example"""
        factors_text = "\n".join([f"• {factor}" for factor in factors])
        
        example = {
            "input": f"What is the likely outcome of this case: {case_description}",
            "context": f"Case Outcome Prediction Request",
            "expected_output": f"""## Case Outcome Prediction

### Case Analysis
{case_description}

### Predicted Outcome
{prediction}

### Confidence Level
{confidence:.1%}

### Key Factors Influencing Prediction
{factors_text}

### Risk Assessment
- **Strengths**: [List favorable factors]
- **Weaknesses**: [List unfavorable factors]
- **Mitigation Strategies**: [Suggest ways to strengthen case]

### Recommendations
Based on this analysis, the recommended course of action is:
- Consider settlement negotiations if confidence is moderate
- Prepare thoroughly for litigation if confidence is high
- Gather additional evidence to strengthen the case""",
            "category": "outcome_prediction",
            "entities": self._extract_entities(case_description)
        }
        self.training_examples.append(example)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction for training data"""
        import re
        
        entities = []
        
        # Extract court names
        courts = re.findall(r'(Supreme Court|High Court|District Court|Sessions Court)', text)
        entities.extend(courts)
        
        # Extract act names
        acts = re.findall(r'([A-Z][a-z]+ Act \d{4})', text)
        entities.extend(acts)
        
        # Extract section references
        sections = re.findall(r'Section \d+[A-Z]?', text)
        entities.extend(sections)
        
        # Extract article references
        articles = re.findall(r'Article \d+[A-Z]?', text)
        entities.extend(articles)
        
        return list(set(entities))  # Remove duplicates
    
    def generate_shreya_singhal_example(self):
        """Add specific Shreya Singhal case example"""
        self.add_case_law_example(
            case_name="Shreya Singhal v. Union of India (2015)",
            facts="The case challenged Section 66A of the Information Technology Act, 2000, which criminalized sending offensive messages through digital platforms.",
            legal_issue="Whether Section 66A violated freedom of speech under Article 19(1)(a) of the Constitution",
            ruling="The Supreme Court struck down Section 66A as unconstitutional, holding it violated the fundamental right to freedom of speech and expression. The court found the provision vague, ambiguous, and not narrowly tailored to protect public interest.",
            citation="(2015) 5 SCC 1"
        )
        
        # Add winning prediction example
        self.add_prediction_example(
            case_description="Shreya Singhal challenged Section 66A of IT Act claiming it violated free speech rights. The government argued the provision was necessary to prevent cyber crimes and protect public order.",
            prediction="Petitioner (Shreya Singhal) would win",
            confidence=0.95,
            factors=[
                "Section 66A was vague and overbroad",
                "Violated fundamental right under Article 19(1)(a)",
                "Not narrowly tailored to achieve objective",
                "Supreme Court precedent favoring free speech",
                "Lack of clear definition for 'offensive' messages"
            ]
        )
    
    def generate_training_dataset(self) -> List[Dict]:
        """Generate comprehensive training dataset"""
        
        # Add Shreya Singhal example
        self.generate_shreya_singhal_example()
        
        # Add constitutional law examples
        self.add_statutory_interpretation_example(
            act_name="Information Technology Act, 2000",
            section="Section 66A (struck down)",
            interpretation="This section previously criminalized sending offensive messages through digital devices but was declared unconstitutional for being vague and overbroad.",
            application="The striking down of this provision strengthened free speech protections in digital spaces in India."
        )
        
        self.add_statutory_interpretation_example(
            act_name="Constitution of India",
            section="Article 19(1)(a)",
            interpretation="Guarantees the fundamental right to freedom of speech and expression, subject to reasonable restrictions under Article 19(2).",
            application="This right forms the basis for challenging laws that unnecessarily restrict speech, including digital communications."
        )
        
        # Add contract law examples
        self.add_case_law_example(
            case_name="Balfour v. Balfour (1919)",
            facts="Husband promised to pay wife £30 per month during separation, but failed to pay. Wife sued for breach.",
            legal_issue="Whether domestic agreements between spouses are legally enforceable contracts",
            ruling="Court held that domestic agreements are not legally enforceable as they lack intention to create legal relations.",
            citation="[1919] 2 KB 571"
        )
        
        # Add prediction examples
        self.add_prediction_example(
            case_description="A software company sues a client for non-payment of ₹50 lakhs for delivered software solutions. The contract has clear payment terms, and the client has acknowledged receipt of services but claims quality issues.",
            prediction="High probability of favorable outcome for the software company",
            confidence=0.85,
            factors=[
                "Written contract with clear payment terms",
                "Acknowledgment of service receipt by client",
                "Specific amount claimed (₹50 lakhs)",
                "Client's quality claims appear to be delaying tactics",
                "Strong documentary evidence available"
            ]
        )
        
        return self.training_examples
    
    def save_training_data(self, filename: str = "enhanced_legal_training_data.json"):
        """Save training data to file"""
        dataset = self.generate_training_dataset()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Enhanced training dataset saved: {filename}")
        print(f"📊 Generated {len(dataset)} training examples")
        
        # Print statistics
        categories = {}
        for example in dataset:
            cat = example['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📈 Training Data Breakdown:")
        for category, count in categories.items():
            print(f"  {category}: {count} examples")
        
        return dataset

# Generate enhanced training data
if __name__ == "__main__":
    generator = LegalTrainingDataGenerator()
    training_data = generator.save_training_data()
    
    print("\n🎯 Training Data Features:")
    print("- Case law analysis with proper citations")
    print("- Statutory interpretation with applications")
    print("- Legal procedures with practical guidance")
    print("- Outcome predictions with confidence scores")
    print("- Entity extraction integrated naturally")
    print("- Professional legal response formatting")
