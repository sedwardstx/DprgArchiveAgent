from pinecone import Pinecone
import inspect

# Try to print the Pinecone version
try:
    import pinecone
    print(f"Pinecone version: {pinecone.__version__}")
except AttributeError:
    print("Pinecone version attribute not available")

# Print all available attributes/classes in the Pinecone module
print("\nAvailable attributes/classes in Pinecone module:")
for name in dir(pinecone):
    if not name.startswith('_'):  # Skip private attributes
        try:
            attr = getattr(pinecone, name)
            if inspect.isclass(attr):
                print(f"Class: {name}")
            elif inspect.isfunction(attr):
                print(f"Function: {name}")
            else:
                print(f"Attribute: {name} (type: {type(attr).__name__})")
        except Exception as e:
            print(f"Error getting attribute {name}: {str(e)}")

# Check Pinecone class
print("\nChecking Pinecone class:")
pinecone_class = Pinecone
print(f"Pinecone class: {pinecone_class}")
print("Methods and attributes of Pinecone class:")
for name in dir(pinecone_class):
    if not name.startswith('_'):  # Skip private attributes
        try:
            attr = getattr(pinecone_class, name)
            if inspect.ismethod(attr) or inspect.isfunction(attr):
                print(f"  Method: {name}")
            else:
                print(f"  Attribute: {name} (type: {type(attr).__name__})")
        except Exception as e:
            print(f"  Error getting attribute {name}: {str(e)}")

# Try to initialize Pinecone
print("\nTrying to initialize Pinecone:")
try:
    # Current method (v2.2.4)
    pc = Pinecone(api_key="test_key")
    print("✓ Pinecone(api_key='test_key') works")
except Exception as e:
    print(f"✗ Error initializing Pinecone: {str(e)}")

# Try to access index
try:
    index = pc.Index("test_index")
    print("✓ pc.Index('test_index') works")
except Exception as e:
    print(f"✗ Error accessing Index: {str(e)}")

# Check if list_indexes is available
try:
    print("\nChecking list_indexes method:")
    if hasattr(pc, 'list_indexes'):
        print("✓ list_indexes method exists")
    else:
        print("✗ list_indexes method does not exist")
except Exception as e:
    print(f"Error checking list_indexes: {str(e)}")

# Check for create_index method
try:
    print("\nChecking create_index method:")
    if hasattr(pc, 'create_index'):
        print("✓ create_index method exists")
    else:
        print("✗ create_index method does not exist")
except Exception as e:
    print(f"Error checking create_index: {str(e)}")

# Check for different specs
print("\nChecking Pinecone specs:")
try:
    from pinecone import ServerlessSpec
    print("✓ ServerlessSpec import worked")
except ImportError:
    print("✗ ServerlessSpec import failed")

try:
    from pinecone import PodSpec
    print("✓ PodSpec import worked")
except ImportError:
    print("✗ PodSpec import failed") 