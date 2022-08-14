from .console import console
import requests


class Utils:
    @staticmethod
    def format_int_to_clp(number: int):
        return "${:,.0f}".format(number).replace(",", ".")

    @classmethod
    def ask_confirmation(
        cls, confirmation, interactive=True, dont_exit: bool = True
    ) -> None:
        """confirmation: str = statement to display in
        the confirmation message.
        If confirmation statement's input is True,
        then the function will return None
        elif False, then the function will return
        a ValueError unless dont_exit is True.
        """
        if interactive == False:
            return
        console.log(confirmation, style="blue bold")
        _input = input("[y/n]: ")
        if _input == "y":
            return
        elif _input == "n":
            if dont_exit:
                console.log(
                    "`dont_exit` flag is on. Must be sensitive"
                    + " data that cant be reverted.",
                    style="red bold",
                )
                return cls.ask_confirmation(confirmation, interactive, dont_exit)
            else:
                raise ValueError("Stopped by user's input.")

    @staticmethod
    def download_file_from_URL(url: str, filePATH: str, **kwargs) -> bool:
        console.log(f"Downloading file to PATH: {filePATH}...")
        full_path = f"{filePATH}"
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            console.log("File donwloaded successfully.", style="green")
            try:
                open(f"{full_path}", "wb").write(r.content)
                return True
            except Exception as e:
                raise ValueError(f"Error while writing file to disk (Error: {e}).")
        else:
            return False
