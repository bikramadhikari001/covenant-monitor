"""Set up database with proper permissions."""
import os
import stat

def setup_database():
    """Create instance directory and set permissions."""
    print("Setting up database...")
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'covenant.db')
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_dir):
        print(f"Creating instance directory: {instance_dir}")
        os.makedirs(instance_dir)
    
    # Set directory permissions (rwxrwxr-x)
    print("Setting directory permissions...")
    os.chmod(instance_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    
    # Create or touch database file
    if not os.path.exists(db_path):
        print(f"Creating database file: {db_path}")
        open(db_path, 'a').close()
    
    # Set file permissions (rw-rw-r--)
    print("Setting database file permissions...")
    os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
    
    print("\nCurrent permissions:")
    print(f"Instance directory: {oct(os.stat(instance_dir).st_mode)[-3:]}")
    print(f"Database file: {oct(os.stat(db_path).st_mode)[-3:]}")
    
    print("\nSetup complete!")

if __name__ == '__main__':
    setup_database()
