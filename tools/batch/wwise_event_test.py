import os
import unreal_engine as ue
from unreal_engine.classes import PythonScriptLibrary

class WwisePerformanceTest:
    def __init__(self):
        self.wwise_audio = PythonScriptLibrary.load_python_module('WwiseAudio')

    def test_audio_performance(self, num_sources, num_events):
        # Set up Wwise audio
        self.wwise_audio.initialize()
        self.wwise_audio.set_soundbank_path('Path/To/Your/Soundbanks')  # Replace with the accurate bank path
        self.wwise_audio.load_bank('Master')  # Replace with the accurate bank name

        # Create actors and attach audio components
        actors = []
        for _ in range(num_sources):
            actor = ue.get_editor_world().spawn_actor_from_class(ue.StaticMeshActor, ue.Transform())
            audio_component = actor.add_component_by_class(ue.AudioComponent)
            audio_component.set_sound(self.wwise_audio.get_event('EventName'))  # Replace with the accurate Wwise event name
            actors.append(actor)

        # Play the events and measure performance
        start_time = ue.get_world_timer_manager().get_real_time_seconds()
        for _ in range(num_events):
            for actor in actors:
                audio_component = actor.get_component_by_class(ue.AudioComponent)
                audio_component.play()
        end_time = ue.get_world_timer_manager().get_real_time_seconds()
        elapsed_time = end_time - start_time
        print(f'Elapsed time: {elapsed_time} seconds')

        # Clean up
        for actor in actors:
            actor.destroy()
        self.wwise_audio.unload_bank('Master')  # Replace with the accurate bank name
        self.wwise_audio.shutdown()

# Run the test
wwise_test = WwisePerformanceTest()
wwise_test.test_audio_performance(num_sources=100, num_events=1000)
print('Wwise Test has been running...')
print('Wwise Test Successfully')