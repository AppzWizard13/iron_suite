import os
import sys
import re

# Automatically detect the base path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_to_django_template(template_path, static_namespace):
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Add {% load static %} if not present
        if "{% load static %}" not in content:
            content = "{% load static %}\n" + content

        # Replace ../assets/ paths
        content = re.sub(
            r"""(?<=["'(=])\.\./assets/""",
            f"{{% static '{static_namespace}/assets/",
            content
        )

        # Replace common static directories with proper {% static %} tag
        static_dirs = ['css', 'js', 'images', 'fonts', 'img']
        for d in static_dirs:
            pattern = re.compile(rf"""(?<=["'(=]){d}/([\w\-/\.]+)""")
            content = pattern.sub(rf"{{% static '{static_namespace}/{d}/\1' %}}", content)

        # Fix broken static tag endings (like "%}" inside quotes)
        content = re.sub(r"""\{%\ static\s+'([^']+?)["'] *%}""", r"{% static '\1' %}", content)

        # Remove any accidental double slashes in generated paths
        content = re.sub(r"/{2,}", "/", content)

        # Ensure correct closing for static tag
        content = re.sub(
            r"""\{%\ static\s+['"]([^'"]+)['"]\s*""",
            r"{% static '\1' %}",
            content
        )

        # Final cleanup for edge cases
        content = content.replace("'%}", "' %}")
        content = content.replace('"%}', "' %}")
        content = content.replace("%%}", "%}")
        content = content.replace("%} %}", "%}")

        with open(template_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"✅ Converted: {template_path}")
        return True

    except Exception as e:
        print(f"❌ Error converting {template_path}: {e}")
        return False


def convert_all_templates(app_name):
    template_root = os.path.join(BASE_DIR, "templates", app_name)

    if not os.path.exists(template_root):
        print(f"❌ Template folder not found: {template_root}")
        return

    html_files = []
    for root, _, files in os.walk(template_root):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    if not html_files:
        print("⚠️ No HTML files found.")
        return

    for html_file in html_files:
        convert_to_django_template(html_file, app_name)

    print(f"\n✅ Done. {len(html_files)} template(s) processed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python STMAKER.py <app_name>")
        print("Example: python STMAKER.py gym_ui")
    else:
        app_name = sys.argv[1]
        convert_all_templates(app_name)
