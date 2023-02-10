import templatoron

if __name__ == '__main__':
    templatoron.generate_templatoron_file_from_folder(
        "project_files_to_scan/@#project_name",
        "templatoron_template_files/pypi-project.json"
    )
    templatoron.create_files_from_templatoron_file(
        "templatoron_template_files/pypi-project.json",
        "",
        project_name="projectr",
        package_name="projectr"
    )