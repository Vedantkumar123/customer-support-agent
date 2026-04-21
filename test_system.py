#!/usr/bin/env python3
#!/usr/bin/env python3

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from bm25_retriever import PineconeRetriever
from sarvam_client import SarvamAPIClient
from prompt_engineer import PromptEngineer, SupportMode


def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_vector_retrieval():
    print_section("Testing Vector Retrieval with Pinecone")
    
    try:
        retriever = PineconeRetriever("backend/policies.json")
        print(f"Loaded {len(retriever.documents)} policies")
        
        test_queries = [
            "refund policy",
            "delivery delay",
            "damaged product",
            "return policy",
            "cancellation"
        ]
        
        for query in test_queries:
            docs, scores = retriever.retrieve(query, top_k=3)
            print(f"\nQuery: '{query}'")
            print("-" * 40)
            for i, (doc, score) in enumerate(zip(docs, scores), 1):
                print(f"{i}. {doc['title']}")
                print(f"   Similarity: {score:.4f}")
    
    except Exception as e:
        print(f"Vector Retrieval Test Failed: {e}")
        return False
    
    return True


def test_prompt_engineering():
    print_section("Testing Prompt Engineering")
    
    try:
        context = """[Policy 1] Refund Policy:
Customers can request refunds within 7 days of delivery."""
        
        query = "Can I get a refund for my order?"
        
        for mode in SupportMode:
            print(f"\n{mode.value.upper()} Mode:")
            print("-" * 40)
            
            prompt = PromptEngineer.get_prompt(mode, context, query)
            config = PromptEngineer.get_config_for_mode(mode)
            
            print(f"Temperature: {config['temperature']}")
            print(f"Max Tokens: {config['max_tokens']}")
            print(f"Prompt Length: {len(prompt)} characters")
            print(f"Preview: {prompt[:100]}...")
        
        print("\nAll prompt templates generated successfully")
    
    except Exception as e:
        print(f"Prompt Engineering Test Failed: {e}")
        return False
    
    return True


def test_sarvam_client():
    print_section("Testing Sarvam AI Client")
    
    try:
        client = SarvamAPIClient()
        
        if client.api_key:
            print("Sarvam API key found")
            print("(Real API will be used)")
        else:
            print("No Sarvam API key found")
            print("(Mock responses will be used)")
        
        test_prompt = "Answer this customer question: What is your refund policy?"
        
        response = client.generate_response(
            prompt=test_prompt,
            temperature=0.7,
            max_tokens=100,
            use_mock=True
        )
        
        print(f"\nMock Response Test:")
        print(f"Success: {response['success']}")
        print(f"Model: {response['model']}")
        print(f"Response Length: {len(response['text'])} chars")
        print(f"\nSample: {response['text'][:100]}...")
    
    except Exception as e:
        print(f"Sarvam Client Test Failed: {e}")
        return False
    
    return True


def test_full_workflow():
    print_section("Testing Full Workflow")
    
    try:
        retriever = PineconeRetriever("backend/policies.json")
        sarvam_client = SarvamAPIClient()
        
        customer_query = "My product arrived late and damaged. Can I get a refund?"
        
        print(f"Customer Query: '{customer_query}'")
        print("-" * 60)
        
        print("\n1. Vector Similarity Search:")
        docs, scores = retriever.retrieve(customer_query, top_k=3)
        max_score = max(scores) if scores else 0
        
        for doc, score in zip(docs, scores):
            print(f"   {doc['title']}: {score:.4f}")
        
        print(f"\n2. Similarity Check:")
        print(f"   Max Score: {max_score:.4f}")
        mode = "fallback" if max_score < 0.5 else "friendly"
        print(f"   Selected Mode: {mode}")
        
        print(f"\n3. Prompt Construction:")
        if mode != "fallback":
            context = retriever.get_document_context(docs)
            prompt = PromptEngineer.get_prompt(
                SupportMode(mode), context, customer_query
            )
        else:
            prompt = PromptEngineer.get_prompt(
                SupportMode.FALLBACK, "", customer_query
            )
        print(f"   Prompt Length: {len(prompt)} chars")
        
        print(f"\n4. LLM Parameters:")
        config = PromptEngineer.get_config_for_mode(SupportMode(mode))
        print(f"   Temperature: {config['temperature']}")
        print(f"   Max Tokens: {config['max_tokens']}")
        
        print(f"\n5. Response Generation (Mock):")
        response = sarvam_client.generate_response(
            prompt=prompt,
            temperature=config['temperature'],
            max_tokens=config['max_tokens'],
            use_mock=True
        )
        print(f"   Success: {response['success']}")
        print(f"   Model: {response['model']}")
        
        print(f"\n6. Generated Response:")
        print(f"   {response['text']}")
        
        print(f"\nFull workflow completed successfully!")
    
    except Exception as e:
        print(f"Full Workflow Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_policies_format():
    print_section("Validating Policies Format")
    
    try:
        with open("backend/policies.json", 'r') as f:
            policies = json.load(f)
        
        print(f"Found {len(policies)} policies\n")
        
        for i, policy in enumerate(policies, 1):
            required_fields = ['id', 'title', 'content']
            missing = [f for f in required_fields if f not in policy]
            
            if missing:
                print(f"Policy {i} missing fields: {missing}")
                return False
            
            print(f"{i}. {policy['title']}")
            print(f"   ID: {policy['id']}")
            print(f"   Content: {len(policy['content'])} chars")
        
        print(f"\nAll policies validated successfully")
    
    except Exception as e:
        print(f"Policy Validation Failed: {e}")
        return False
    
    return True


def main():
    print("\n" + "="*60)
    print("  CUSTOMER SUPPORT AI - SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Policies Format", test_policies_format),
        ("Vector Retrieval", test_vector_retrieval),
        ("Prompt Engineering", test_prompt_engineering),
        ("Sarvam AI Client", test_sarvam_client),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\nUnexpected error in {test_name}: {e}")
            results[test_name] = False
    
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
