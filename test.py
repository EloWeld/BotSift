import json
from pyrogram import Client

from etc.keyboards import Keyboards

# Create a Pyrogram client with a name and API ID and key
app = Client(
    "my_bot",
    api_id=12345,
    api_hash="0123456789abcdef0123456789abcdef",
    session_string="AgDjbrUAqm0tB3SBbVys8_HCg_WWt213L9F-eAq44Yg1b8cn1Yt12-Q6v7oEW7IhY-RazwUS_inkSIC1Q1DDEsNKgRkj5MlpZxm98uh-Mq5_yfZg-PFT-ugcbIulTtIJcgL4v7ad07YJ9LmSgqH7qcGkxJIwrSEGYPB-kU6dXL9UBb9vnHTv9bg8jlLdQ3q0aHEedhToePuJ4fz978TyVSaGBjnJsf6sS8ODZqkIF2FW-W2UKsK0IVZWXS4zr52gTF4OX7bQsmvRPxZMUOfMJQrd6BpyLECkW_xwCdX_po8oHHgwel-HPyigVYW98FBsSrXQOIiQHL29w-3_aVSc97RbKTqkfQAAAAB7EjEWAA"
)

# Initialize the Pyrogram database
app.start()

# Store a chat or user ID in the database
#app.forward_messages(-1001832567943, -1001597758982, 1081)
#app.forward_messages(-1001832567943, -1001832567943, 10)


# Stop the Pyrogram client
app.stop()