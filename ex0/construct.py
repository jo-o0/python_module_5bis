import sys
    #sys.executable     # which python is running
    #sys.prefix         # env's install path (your venv detector!)
    #sys.base_prefix    # path to the base Python that the venv was cloned from — the global one.
    #sys.argv           # command-line arguments
    #sys.exit()         # kill the program (your fail-fast guard)
    #sys.path           # where Python looks for imports
import os
    #os.environ                    # environment variables (ex1's whole personality!)
    #os.environ.get("API_KEY")     # read a secret from the environment
    #os.getcwd()                   # current working directory
    #os.path.exists("file.txt")    # does this file exist?
    #os.listdir(".")               # files in a folder
import site
    #site.getsitepackages()      # list of global site-packages paths
    #site.getusersitepackages()  # user-level site-packages


def is_virtual() -> bool:
    return sys.prefix != sys.base_prefix
        #sys.prefix == sys.base_prefix   →  GLOBAL environment
        #sys.prefix != sys.base_prefix   →  VIRTUAL environment


def main() -> None:
    if is_virtual():
        print("\nMATRIX STATUS: Welcome to the construct\n")
        print("Current Python", sys.executable)
        print("Virtual Environment:", os.path.basename(sys.prefix))
        print("\nSUCCESS: You are in an isolated environment!\n")
        print("Safe to install packages without affecting the global system.")
        print("\nPackage installation path:", site.getsitepackages()[0])
    else:
        print("\nMATRIX STATUS: You are plugged in\n")
        print("Current Python", sys.executable)
        print("Virtual Environment: None detected")
        print("WARNING: You are in the global environment\n"
              "The machines can see everything you install!!\n")
        print("To enter the construct run: "
              "python3 -m venv matrix_env\n"
              "source matrix_env/bin/activate # On Unix\n"
              r"matrix_env\Scripts\activate # On Windows"
              "\n\nThen run this program again.")

if __name__ == "__main__":
    main()
