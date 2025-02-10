
import sys
from vespa.application import Vespa
import numpy as np


def main():
    if (len(sys.argv) < 2):
        print("The script takes one argument, the id of the user")
        return

    userId = sys.argv[1]

    app = Vespa(url = "http://localhost/", port = 8080)

    response = app.feed_data_point(
        schema="user",
        data_id=userId,
        fields={
            "user_id": userId,
            "embedding": np.random.uniform(-1, 1, 50).tolist()
        }
    )
    if (response.is_successful()):
        print("User added!")
    else:
        print("Failed to add user")
        print(response.get_json())

if __name__ == "__main__":
    main()
