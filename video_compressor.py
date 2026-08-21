#!/usr/bin/env python3
"""
Módulo para comprimir videos usando ffmpeg
"""

import subprocess
import os
import logging

logger = logging.getLogger(__name__)


class VideoCompressor:
    """Clase para comprimir videos"""
    
    # Configuración de calidad
    QUALITY_PRESETS = {
        'low': {
            'crf': 28,  # Rango 0-51, mayor = más compresión
            'preset': 'slow',  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
            'resolution': '640:480'
        },
        'medium': {
            'crf': 23,
            'preset': 'medium',
            'resolution': '1280:720'
        },
        'high': {
            'crf': 18,
            'preset': 'slow',
            'resolution': '1920:1080'
        }
    }
    
    def __init__(self):
        """Inicializar compresor"""
        self.check_ffmpeg()
    
    def check_ffmpeg(self) -> bool:
        """Verificar que FFmpeg está instalado"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            logger.info("✓ FFmpeg detectado")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("✗ FFmpeg no está instalado")
            raise RuntimeError("FFmpeg debe estar instalado para usar este bot")
    
    def compress(self, input_path: str, output_path: str, quality: str = 'medium') -> bool:
        """
        Comprimir un video
        
        Args:
            input_path: Ruta del video original
            output_path: Ruta del video comprimido
            quality: Calidad ('low', 'medium', 'high')
        
        Returns:
            True si fue exitoso, False si falló
        """
        if quality not in self.QUALITY_PRESETS:
            logger.warning(f"Calidad no válida: {quality}. Usando 'medium'")
            quality = 'medium'
        
        preset = self.QUALITY_PRESETS[quality]
        
        # Comando FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',  # Codec de video
            '-crf', str(preset['crf']),  # Calidad
            '-preset', preset['preset'],  # Velocidad de compresión
            '-c:a', 'aac',  # Codec de audio
            '-b:a', '128k',  # Bitrate de audio
            '-vf', f"scale={preset['resolution']}:force_original_aspect_ratio=decrease",  # Escalar
            '-y',  # Sobrescribir sin preguntar
            output_path
        ]
        
        try:
            logger.info(f"Comprimiendo {input_path} → {output_path} (Calidad: {quality})")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora máximo
            )
            
            if result.returncode != 0:
                logger.error(f"Error FFmpeg: {result.stderr}")
                return False
            
            logger.info(f"✓ Video comprimido exitosamente")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Tiempo de compresión agotado")
            return False
        except Exception as e:
            logger.error(f"Error durante la compresión: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Obtener información del video
        
        Args:
            video_path: Ruta del video
        
        Returns:
            Diccionario con información del video
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration,codec_name',
                '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = result.stdout.strip().split('\n')
                return {
                    'width': info[0] if len(info) > 0 else 'N/A',
                    'height': info[1] if len(info) > 1 else 'N/A',
                    'duration': info[2] if len(info) > 2 else 'N/A',
                    'codec': info[3] if len(info) > 3 else 'N/A'
                }
        except Exception as e:
            logger.error(f"Error obteniendo información: {e}")
        
        return {}
