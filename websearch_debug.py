# websearch example - DEBUG VERSION
def components_websearchcomponent_invoke():
    from components import WebSearchComponent
    
    websearch = WebSearchComponent()
    
    print("🔍 TESTING WEBSEARCH COMPONENT - DEBUG MODE")
    print("=" * 60)
    
    # Test 1: Original AI query
    print("\n📋 TEST 1: Original AI Query")
    input_cro1 = ComponentResultObject()
    input_cro1["content"]["original_text"] = "artificial intelligence latest developments 2025"
    input_cro1["content"]["page_count"] = 3
    
    print(f"Query: {input_cro1['content']['original_text']}")
    results1 = websearch.invoke([input_cro1])
    
    print(f"Found {len(results1)} results:")
    for i, result in enumerate(results1):
        print(f"  {i+1}. Title: {result['content']['title']}")
        print(f"     URL: {result['source']}")
        print(f"     Preview: {result['content']['original_text'][:100]}...")
        print()
    
    # Test 2: Simple AI query
    print("\n📋 TEST 2: Simple AI Query")
    input_cro2 = ComponentResultObject()
    input_cro2["content"]["original_text"] = "artificial intelligence"
    input_cro2["content"]["page_count"] = 3
    
    print(f"Query: {input_cro2['content']['original_text']}")
    results2 = websearch.invoke([input_cro2])
    
    print(f"Found {len(results2)} results:")
    for i, result in enumerate(results2):
        print(f"  {i+1}. Title: {result['content']['title']}")
        print(f"     URL: {result['source']}")
        print(f"     Preview: {result['content']['original_text'][:100]}...")
        print()
    
    # Test 3: Machine Learning query  
    print("\n📋 TEST 3: Machine Learning Query")
    input_cro3 = ComponentResultObject()
    input_cro3["content"]["original_text"] = "machine learning"
    input_cro3["content"]["page_count"] = 3
    
    print(f"Query: {input_cro3['content']['original_text']}")
    results3 = websearch.invoke([input_cro3])
    
    print(f"Found {len(results3)} results:")
    for i, result in enumerate(results3):
        print(f"  {i+1}. Title: {result['content']['title']}")
        print(f"     URL: {result['source']}")
        print(f"     Preview: {result['content']['original_text'][:100]}...")
        print()
    
    # Test 4: Exact search terms from ReasoningAgent
    print("\n📋 TEST 4: Exact ReasoningAgent Search Terms")
    
    test_terms = [
        "artificial intelligence machine learning data processing",
        "human intelligence cognitive abilities"
    ]
    
    for term in test_terms:
        print(f"\nTesting: '{term}'")
        input_cro = ComponentResultObject()
        input_cro["content"]["original_text"] = term
        input_cro["content"]["page_count"] = 3
        
        results = websearch.invoke([input_cro])
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  {i+1}. Title: {result['content']['title']}")
            print(f"     URL: {result['source']}")
            print()
    
    print("=" * 60)
    print("🔍 WEBSEARCH COMPONENT DEBUG TEST COMPLETE")

