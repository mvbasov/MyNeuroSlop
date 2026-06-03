import sys

def patch_file():
    input_file = "bip39_converter_v1_13_0.html"
    output_file = "bip39_converter_v1_14_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # 1. Bump version
    content = content.replace("v1.13.0", "v1.14.0")

    # 2. Replace Base64 Data URI with URI encoded version
    search_str = r"""    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBwb2ludHM9IjUwLDUgOTAsMjUgOTAsNzUgNTAsOTUgMTAsNzUgMTAsMjUiIGZpbGw9IiMwMDdiZmYiLz48dGV4dCB4PSI1MCIgeT0iNjUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNDAiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSIjZmZmZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj4zOTwvdGV4dD48L3N2Zz4=">"""

    replace_str = r"""    <link class="favicon-link" rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20100%20100%22%3E%3Cpolygon%20points%3D%2250%2C5%2090%2C25%2090%2C75%2050%2C95%2010%2C75%2010%2C25%22%20fill%3D%22%23007bff%22%2F%3E%3Ctext%20x%3D%2250%22%20y%3D%2265%22%20font-family%3D%22system-ui%2C-apple-system%2Csans-serif%22%20font-size%3D%2240%22%20font-weight%3D%22bold%22%20fill%3D%22%23ffffff%22%20text-anchor%3D%22middle%22%3E39%3C%2Ftext%3E%3C%2Fsvg%3E">"""

    if search_str not in content:
        print("Error: Favicon link not found. Ensure you are using v1.13.0.")
    else:
        content = content.replace(search_str, replace_str)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    patch_file()