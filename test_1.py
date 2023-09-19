import yaml
#from checkers import checkout, check_hash_crc32
from sshcheckers import ssh_checkout, upload_files, ssh_getout
import pytest

with open('config.yaml') as fy:
    data = yaml.safe_load(fy)


class TestPositive:
    def save_log(self, start_time, name):
        with open(name, 'a') as f:
            f.write(ssh_getout(data["ip"], data["user"], data["passwd"], f"journalctl --since '{start_time}'"))

    def test_deploy(self, start_time):
        res = []
        upload_files(data["ip"], data["user"], data["passwd"], f'tests/{data["pkgname"]}.deb',
                     f'/home/{data["user"]}/{data["pkgname"]}.deb')
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f'echo "{data["passwd"]}" | sudo -S dpkg -i /home/{data["user"]}/{data["pkgname"]}.deb',
                                "Настраивается пакет"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"],
                                f'echo "{data["passwd"]}" | sudo -S dpkg -s {data["pkgname"]}',
                                "Status: install ok installed"))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_deploy FAIL"

    def test_add_archive(self, make_folder, clear_folder, make_files, start_time):  # a создали архив
        res_add = ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok")
        res_ls = ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_out"]}', f'arx2.{data["arc_type"]}')
        self.save_log(start_time, "log_positive.txt")
        assert res_add and res_ls, "test_add_archive FAIL"

    def test_check_e_extract(self, clear_folder, make_files, start_time):  #
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z e arx2.{data["arc_type"]} -o{data["folder_ext"]} -y', "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', item))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_check_e_extract FAIL"

    def test_check_e_extract_subfolder(self, clear_folder, make_files, make_subfolder, start_time):
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z e arx2.{data["arc_type"]} -o{data["folder_ext"]} -y', "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', item))
        for item in make_subfolder:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', item))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_check_e_extract_subfolder FAIL"

    def test_check_x_extract_subfolder(self, clear_folder, make_files, make_subfolder, start_time):
        # files, subflder and files in subfolder
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z x arx2.{data["arc_type"]} -o{data["folder_ext"]} -y', "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', item))

        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', make_subfolder[0]))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}/{make_subfolder[0]}', make_subfolder[1]))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_check_e_extract_subfolder FAIL"

    def test_check_x_files(self, clear_folder, make_files, start_time):  # only files
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z x arx2.{data["arc_type"]} -o{data["folder_ext"]} -y', "Everything is Ok"))
        for item in make_files:
            res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'ls {data["folder_ext"]}', item))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_check_x_files FAIL"

    def test_totality(self, clear_folder, make_files, start_time):  # t проверка целостности архива
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z t arx2.{data["arc_type"]}', "Everything is Ok"))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_totality FAIL"

    def test_delete(self, clear_folder, make_files, make_subfolder, start_time):  # d удаление из архива
        res = list()
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok"))
        res.append(ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_out"]}; 7z d arx2.{data["arc_type"]}', "Everything is Ok"))
        self.save_log(start_time, "log_positive.txt")
        assert all(res), "test_delete FAIL"

    def test_update(self, start_time):# u - обновление архива
        self.save_log(start_time, "log_positive.txt")
        assert (ssh_checkout(data["ip"], data["user"], data["passwd"], f'cd {data["folder_in"]}; 7z u {data["folder_out"]}/arx2.{data["arc_type"]}', "Everything is Ok"), 'NO update'), "test_update FAIL"


if __name__ == '__main__':
    pytest.main(['-v'])