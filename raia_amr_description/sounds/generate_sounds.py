#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  GÉNÉRATEUR DE SIGNAUX AUDIO INDUSTRIELS — RAIA AMR (NORME ISO 3691-4)
  1. amr_patrol_melody.wav  : Musique instrumentale mélodique douce (40% vol)
                              jouée en continu le long du parcours
  2. amr_obstacle_alarm.wav : Avertisseur sonore industriel puissant (98% vol)
                              déclenché immédiatement lors d'un obstacle
  3. amr_arrival_chime.wav  : Carillon d'arrivée en station (50% vol)
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import wave
import struct
import math


def generate_patrol_melody(filepath: str, sample_rate: int = 44100):
    """
    Génère une mélodie instrumentale harmonieuse (type marimba / synthétiseur doux).
    Arpège en Do majeur / La mineur pentatonique, volume modéré (~40%).
    """
    # Notes : [fréquence Hz, durée s]
    melody = [
        (261.63, 0.45),  # C4
        (329.63, 0.45),  # E4
        (392.00, 0.45),  # G4
        (440.00, 0.45),  # A4
        (523.25, 0.45),  # C5
        (440.00, 0.45),  # A4
        (392.00, 0.45),  # G4
        (329.63, 0.45),  # E4
    ]

    total_duration = sum(dur for _, dur in melody)
    samples = []
    amplitude = 0.38 * 32767  # Volume modéré (38%)

    for freq, dur in melody:
        note_samples = int(sample_rate * dur)
        attack = int(sample_rate * 0.03)
        decay = int(sample_rate * 0.05)
        release = int(sample_rate * 0.08)

        for i in range(note_samples):
            if i < attack:
                env = i / attack
            elif i < attack + decay:
                env = 1.0 - 0.25 * ((i - attack) / decay)
            elif i > note_samples - release:
                env = 0.75 * ((note_samples - i) / release)
            else:
                env = 0.75

            t = i / sample_rate
            # Fondamentale + 2ème harmonique subtile
            val = env * (
                0.75 * math.sin(2.0 * math.pi * freq * t) +
                0.20 * math.sin(2.0 * math.pi * (2.0 * freq) * t) +
                0.05 * math.sin(2.0 * math.pi * (3.0 * freq) * t)
            )
            sample_val = int(amplitude * val)
            sample_val = max(-32768, min(32767, sample_val))
            samples.append(sample_val)

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        raw_data = struct.pack(f"<{len(samples)}h", *samples)
        wav_file.writeframes(raw_data)

    print(f"[OK] Fichier généré : {filepath} ({len(samples)/sample_rate:.2f}s, vol ~40%)")


def generate_obstacle_alarm(filepath: str, sample_rate: int = 44100):
    """
    Génère un signal sonore d'avertissement industriel puissant et percutant.
    Sirène alternée deux-tons (1046 Hz / 1318 Hz) à plein volume (98% amplitude).
    """
    amplitude = 0.96 * 32767  # Volume très élevé (+10 dB par rapport à la mélodie)

    # 4 bips d'alarme puissants alternés : C6 (1046.5 Hz) et E6 (1318.5 Hz)
    beeps = [
        (1046.5, 0.22, 0.04),
        (1318.5, 0.22, 0.04),
        (1046.5, 0.22, 0.04),
        (1318.5, 0.22, 0.06),
    ]

    samples = []

    for freq, sound_dur, silence_dur in beeps:
        sound_samples = int(sample_rate * sound_dur)
        silence_samples = int(sample_rate * silence_dur)

        attack = int(sample_rate * 0.01)
        decay = int(sample_rate * 0.02)

        for i in range(sound_samples):
            if i < attack:
                env = i / attack
            elif i > sound_samples - decay:
                env = (sound_samples - i) / decay
            else:
                env = 1.0

            t = i / sample_rate
            val = env * (
                0.70 * math.sin(2.0 * math.pi * freq * t) +
                0.20 * math.sin(2.0 * math.pi * (2.0 * freq) * t) +
                0.10 * math.sin(2.0 * math.pi * (3.0 * freq) * t)
            )
            sample_val = int(amplitude * val)
            sample_val = max(-32768, min(32767, sample_val))
            samples.append(sample_val)

        for _ in range(silence_samples):
            samples.append(0)

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        raw_data = struct.pack(f"<{len(samples)}h", *samples)
        wav_file.writeframes(raw_data)

    print(f"[OK] Fichier généré : {filepath} ({len(samples)/sample_rate:.2f}s, vol ~98% PUISSANT)")


def generate_arrival_chime(filepath: str, sample_rate: int = 44100):
    """
    Carillon d'arrivée deux-tons (C5 523Hz -> G5 784Hz) annonçant l'amarrage / arrêt.
    """
    amplitude = 0.50 * 32767
    chimes = [
        (523.25, 0.40),  # C5
        (783.99, 0.70),  # G5
    ]
    samples = []
    for freq, dur in chimes:
        note_samples = int(sample_rate * dur)
        attack = int(sample_rate * 0.02)
        decay = int(sample_rate * 0.30)
        for i in range(note_samples):
            if i < attack:
                env = i / attack
            else:
                env = math.exp(-3.0 * (i - attack) / note_samples)
            t = i / sample_rate
            val = env * (
                0.80 * math.sin(2.0 * math.pi * freq * t) +
                0.20 * math.sin(2.0 * math.pi * 2.0 * freq * t)
            )
            sample_val = int(amplitude * val)
            sample_val = max(-32768, min(32767, sample_val))
            samples.append(sample_val)

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        raw_data = struct.pack(f"<{len(samples)}h", *samples)
        wav_file.writeframes(raw_data)

    print(f"[OK] Fichier généré : {filepath} ({len(samples)/sample_rate:.2f}s, vol ~50%)")


def main():
    sounds_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(sounds_dir, exist_ok=True)

    melody_path = os.path.join(sounds_dir, "amr_patrol_melody.wav")
    alarm_path = os.path.join(sounds_dir, "amr_obstacle_alarm.wav")
    chime_path = os.path.join(sounds_dir, "amr_arrival_chime.wav")

    print("═══════════════════════════════════════════════════════════════")
    print(" GÉNÉRATION DES FLUX AUDIO INDUSTRIELS RAIA AMR")
    print("═══════════════════════════════════════════════════════════════")
    generate_patrol_melody(melody_path)
    generate_obstacle_alarm(alarm_path)
    generate_arrival_chime(chime_path)
    print("═══════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
