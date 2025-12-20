import subprocess
import os

def test_multi_speaker():
    script = "Joe: Hey Jane, did you see the new update?\nJane: Yes Joe, it looks amazing! The voice quality is incredible."
    
    cmd = [
        "gen-tts",
        script,
        "--multi-speaker",
        "--speaker-voices", "Joe=Kore", "Jane=Puck",
        "--output-file", "multi_speaker_test.wav",
        "--no-play"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        if os.path.exists("multi_speaker_test.wav"):
            print("Success: 'multi_speaker_test.wav' was created.")
            # Clean up
            os.remove("multi_speaker_test.wav")
        else:
            print("Failure: Output file was not created.")
    except subprocess.CalledProcessError as e:
        print(f"Error running gen-tts: {e}")

if __name__ == "__main__":
    test_multi_speaker()

