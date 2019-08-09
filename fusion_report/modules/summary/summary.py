from fusion_report.modules.base_module import BaseModule


class CustomModule(BaseModule):

    def load(self):
        return {
            'tools': self.manager.get_running_tools(),
            'num_detected_fusions': len(self.manager.get_fusions()),
            'num_known_fusions': len(self.manager.get_known_fusions())
        }
