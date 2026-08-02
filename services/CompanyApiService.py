import requests

class CompanyApiService:

    API_URL = "http://127.0.0.1:8000/empresas/"

    @staticmethod
    def listCompanies() -> list[dict]:
        response = requests.get(CompanyApiService.API_URL, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def createTask(companyId: int, taskData: dict) -> dict:
        url = f"{CompanyApiService.API_URL}{companyId}/tasks/"
        response = requests.post(url, json=taskData, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def listTasks(companyId: int) -> list[dict]:
        url = f"{CompanyApiService.API_URL}{companyId}/tasks/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def updateTask(companyId: int, taskId: int, taskData: dict) -> dict:
        url = f"{CompanyApiService.API_URL}{companyId}/tasks/{taskId}"
        response = requests.put(url, json=taskData, timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def deleteTask(companyId: int, taskId: int) -> None:
        url = f"{CompanyApiService.API_URL}{companyId}/tasks/{taskId}"
        response = requests.delete(url, timeout=10)
        response.raise_for_status()

    @staticmethod
    def addSystemLogin(companyId: int, systemName: str, login: str, password: str) -> dict:
        url = f"{CompanyApiService.API_URL}{companyId}/system-logins/"
        payload = {"system_name": systemName, "login": login, "password": password}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()