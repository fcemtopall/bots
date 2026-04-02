import os
import asyncio
import logging
import importlib
from openclaw import ClawdBot, AnthropicProvider

try:
    import cmdop.exceptions
    cmdop.exceptions.TimeoutError = TimeoutError
except ImportError:
    pass

# Disaster Pattern Koruması 1: Katı Loglama. Hata olursa iz bırakmalı.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Sistem başlatılıyor: Ortam değişkenleri kontrol ediliyor...")

    # 1. Konfigürasyonları Çek
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    active_skills_raw = os.getenv("ACTIVE_SKILLS")
    private_key = os.getenv("PRIVATE_KEY")
    max_position = os.getenv("MAX_POSITION_SIZE_PCT")

    if not all([claude_api_key, active_skills_raw, private_key]):
        logger.error("KRİTİK HATA (Disaster): .env eksik. Bot durduruluyor.")
        return

    active_skills = [s.strip() for s in active_skills_raw.split(",")]
    logger.info(f"Bu sunucuya atanmış yetenekler: {active_skills}")

    try:
        # 2. Claude + OpenClaw Bağlantısı
        # 0x8dxd'nin risk yönetimi yaklaşımını korumak için sistem promptunu katı tutuyoruz
        provider = AnthropicProvider(api_key=claude_api_key, model="claude-3-opus-20240229")
        bot = ClawdBot(
            llm_provider=provider,
            system_prompt=f"Sen otonom bir finansal ajansın. Max pozisyon riskin %{max_position}. "
                          "Sadece EV > 5% olan işlemlere gir. Sermayeyi korumak birinci önceliğindir."
        )

        # 3. İzole Skilleri Yükle
        for skill_name in active_skills:
            try:
                # Modülü dinamik olarak skills klasöründen içeri aktar
                module = importlib.import_module(f"skills.{skill_name}")
                bot.register_skill(module.Skill())
                logger.info(f"[BAŞARILI] Yetenek yüklendi: {skill_name}")
            except Exception as e:
                logger.error(f"SKILL YÜKLEME HATASI ({skill_name}): {e}")
                # Hatalı skill tüm botu patlatmasın diye yola devam et
                continue

        # 4. Ana Döngüyü Başlat (Sonsuz Döngü)
        logger.info("Tüm sistemler devrede. Piyasa dinleniyor...")
        await bot.run_async()

    except Exception as e:
        # Disaster Pattern Koruması 2: Çökme anında yakala
        logger.critical(f"SİSTEM ÇÖKTÜ (Disaster Pattern Tetiklendi): {str(e)}")
        # Not: Telegram acil durum bildirim fonksiyonu buraya eklenecek

if __name__ == "__main__":
    # Disaster Pattern Koruması 3: Asyncio Event Loop kilitlenmesini engelleme
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sistem manuel olarak durduruldu.")