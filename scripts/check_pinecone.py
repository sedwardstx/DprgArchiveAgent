import pinecone
import inspect

# Try to print the Pinecone version
try:
    print(f"Pinecone version: {pinecone.__version__}")
except AttributeError:
    print("Pinecone version attribute not available")

# Print all available attributes/classes in the Pinecone module
print("\nAvailable attributes/classes in Pinecone:")
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

# Try to import directly
print("\nTrying direct imports:")
try:
    from pinecone import Client
    print("✓ Client import worked")
except ImportError:
    print("✗ Client import failed")

try:
    from pinecone import Index
    print("✓ Index import worked")
except ImportError:
    print("✗ Index import failed")
    
# Try to initialize Pinecone
print("\nTrying to initialize Pinecone:")
try:
    # Method 1: Traditional init
    if hasattr(pinecone, 'init'):
        pinecone.init(api_key="test_key")
        print("✓ pinecone.init() exists")
    else:
        print("✗ pinecone.init() does not exist")
        
    # Method 2: Client class
    if hasattr(pinecone, 'Client'):
        client = pinecone.Client(api_key="test_key")
        print("✓ pinecone.Client() exists")
    else:
        print("✗ pinecone.Client() does not exist")
except Exception as e:
    print(f"Error initializing: {str(e)}")

# Try to access specific classes that we're interested in
try:
    print("\nChecking specific classes:")
    for cls_name in ['Pinecone', 'Index', 'GRPCIndex', 'PineconeGRPC']:
        if hasattr(pinecone, cls_name):
            print(f"✓ {cls_name} exists")
        else:
            print(f"✗ {cls_name} does not exist")
except Exception as e:
    print(f"Error checking classes: {str(e)}") 