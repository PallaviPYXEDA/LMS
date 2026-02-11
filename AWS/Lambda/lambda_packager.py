from zipfile import ZipFile

from Lambda import path_resolver


def write_all_dependent_files(zip_file, files):
    for file in files:
        output_file = str.split(file, "/")
        arcname = output_file[-1]
        zip_file.write(file, arcname)


def write_all_dependent_modules(zip_file, modules):
    for module in modules:
        zip_file.write(module, module)


def write_primary_file(zip_file, file):
    arcname = "lambda_function.py"
    zip_file.write(file, arcname)


def prepare_zip_file(function, mappings, input_dir, output_dir):
    zip_file_name = output_dir + function + ".zip"
    with ZipFile(zip_file_name, "w") as zip_file:
        # Add all the dependent files
        main_file = mappings["main"]
        deps = path_resolver.resolve_dependencies(main_file)
        if deps:
            write_all_dependent_modules(zip_file, deps)

        # Write the main file as lambda_function.py
        write_primary_file(zip_file, input_dir + mappings["main"])
