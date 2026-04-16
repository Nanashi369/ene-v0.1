import subprocess


class SkillRegistry:
    def __init__(self):
        self._skills = {
            "open_notepad": self._open_notepad,
            "open_calculator": self._open_calculator,
        }

    def list_skills(self):
        return sorted(self._skills.keys())

    def run(self, name: str):
        fn = self._skills.get(name)
        if not fn:
            return f"Skill '{name}' não encontrada."
        try:
            return fn()
        except Exception as e:
            return f"Falha ao executar skill '{name}': {e}"

    def _open_notepad(self):
        subprocess.Popen(["notepad.exe"])
        return "Skill executada: bloco de notas aberto."

    def _open_calculator(self):
        subprocess.Popen(["calc.exe"])
        return "Skill executada: calculadora aberta."

