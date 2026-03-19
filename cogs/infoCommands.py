import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime
import gc
import io
import uuid

class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "http://raw.thug4ff.xyz/info"
        self.generate_url = "http://profile.thug4ff.xyz/api/profile"
        self.session = aiohttp.ClientSession()
        self.cooldowns = {}

    def convert_unix_timestamp(self, timestamp: int) -> str:
        try:
            return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "Unknown"

    # =====================
    # !info / /info
    # =====================
    @commands.hybrid_command(name="info", description="🎮 Player info | معلومات لاعب Free Fire")
    @app_commands.describe(uid="Free Fire UID")
    async def player_info(self, ctx: commands.Context, uid: str):
        if not uid.isdigit() or len(uid) < 6:
            embed = discord.Embed(color=0xFF0000)
            embed.add_field(name="❌ خطأ | Error", value="الـ UID يجب أن يكون أرقام فقط (6+ خانات)\nUID must be numbers only (6+ digits)", inline=False)
            return await ctx.reply(embed=embed, mention_author=False)

        cooldown = 30
        if ctx.author.id in self.cooldowns:
            last_used = self.cooldowns[ctx.author.id]
            remaining = cooldown - (datetime.now() - last_used).seconds
            if remaining > 0:
                embed = discord.Embed(color=0xFFA500)
                embed.description = f"⏳ انتظر {remaining} ثانية | Wait {remaining}s"
                return await ctx.send(embed=embed, ephemeral=True)

        self.cooldowns[ctx.author.id] = datetime.now()

        try:
            async with ctx.typing():
                async with self.session.get(f"{self.api_url}?uid={uid}&key=great") as response:
                    if response.status == 404:
                        embed = discord.Embed(color=0xFF0000)
                        embed.description = f"❌ اللاعب `{uid}` غير موجود | Player not found"
                        return await ctx.send(embed=embed)
                    if response.status != 200:
                        embed = discord.Embed(color=0xFF0000)
                        embed.description = "⚠️ خطأ في الـ API، حاول لاحقاً | API error, try again later"
                        return await ctx.send(embed=embed)
                    data = await response.json()

            basic_info = data.get('basicInfo', {})
            clan_info = data.get('clanBasicInfo', {})
            captain_info = data.get('captainBasicInfo', {})
            credit_info = data.get('creditScoreInfo', {})
            pet_info = data.get('petInfo', {})
            profile_info = data.get('profileInfo', {})
            social_info = data.get('socialInfo', {})

            embed = discord.Embed(
                title=f"🎮 {basic_info.get('nickname', 'Unknown')}",
                color=0x00BFFF,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            # Basic Info
            embed.add_field(name="📋 معلومات الحساب | Account Info", value="\n".join([
                f"**🆔 UID:** `{uid}`",
                f"**👤 الاسم | Name:** {basic_info.get('nickname', 'N/A')}",
                f"**⭐ اللفل | Level:** {basic_info.get('level', 'N/A')}",
                f"**❤️ لايك | Likes:** {basic_info.get('liked', 'N/A')}",
                f"**🌍 المنطقة | Region:** {basic_info.get('region', 'N/A')}",
                f"**📝 البايو | Bio:** {social_info.get('signature', 'None') or 'None'}",
                f"**🏅 Honor Score:** {credit_info.get('creditScore', 'N/A')}",
            ]), inline=False)

            # Activity
            embed.add_field(name="📊 النشاط | Activity", value="\n".join([
                f"**🏆 BR Rank:** {basic_info.get('rankingPoints', 'N/A')}",
                f"**⚔️ CS Rank:** {basic_info.get('csRankingPoints', 'N/A')}",
                f"**📅 تاريخ الإنشاء | Created:** {self.convert_unix_timestamp(basic_info.get('createAt', 0))}",
                f"**🕐 آخر دخول | Last Login:** {self.convert_unix_timestamp(basic_info.get('lastLoginAt', 0))}",
            ]), inline=False)

            # Pet Info
            if pet_info:
                embed.add_field(name="🐾 البت | Pet", value="\n".join([
                    f"**اسم | Name:** {pet_info.get('name', 'N/A')}",
                    f"**لفل | Level:** {pet_info.get('level', 'N/A')}",
                    f"**XP:** {pet_info.get('exp', 'N/A')}",
                ]), inline=True)

            # Guild Info
            if clan_info:
                embed.add_field(name="🏰 الجيلد | Guild", value="\n".join([
                    f"**اسم | Name:** {clan_info.get('clanName', 'N/A')}",
                    f"**لفل | Level:** {clan_info.get('clanLevel', 'N/A')}",
                    f"**الأعضاء | Members:** {clan_info.get('memberNum', '?')}/{clan_info.get('capacity', '?')}",
                ]), inline=True)

            embed.set_footer(text="FF Info Bot 🎮 | !info <uid>")
            await ctx.send(embed=embed)

            # Send outfit image
            try:
                image_url = f"{self.generate_url}?uid={uid}"
                async with self.session.get(image_url) as img_file:
                    if img_file.status == 200:
                        with io.BytesIO(await img_file.read()) as buf:
                            file = discord.File(buf, filename=f"outfit_{uuid.uuid4().hex[:8]}.png")
                            await ctx.send(file=file)
            except Exception as e:
                print(f"Image error: {e}")

        except Exception as e:
            await ctx.send(f"⚠️ خطأ غير متوقع | Unexpected error: `{e}`")
        finally:
            gc.collect()

    # =====================
    # !help / /help
    # =====================
    @commands.hybrid_command(name="help", description="📖 عرض الأوامر | Show all commands")
    async def help_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📖 قائمة الأوامر | Commands List",
            color=0x00BFFF,
            timestamp=datetime.now()
        )

        embed.add_field(name="🎮 Free Fire", value="\n".join([
            "`!info <uid>` - معلومات لاعب | Player info",
        ]), inline=False)

        embed.add_field(name="🛡️ إدارة | Moderation", value="\n".join([
            "`!kick @user [سبب]` - طرد عضو | Kick member",
            "`!ban @user [سبب]` - حظر عضو | Ban member",
            "`!unban <id>` - رفع الحظر | Unban member",
            "`!clear <عدد>` - حذف رسائل | Clear messages",
            "`!mute @user` - كتم عضو | Mute member",
            "`!unmute @user` - رفع الكتم | Unmute member",
        ]), inline=False)

        embed.add_field(name="👋 ترحيب | Welcome", value="\n".join([
            "`!setwelcome #روم` - تعيين روم الترحيب | Set welcome channel",
            "`!setgoodbye #روم` - تعيين روم الوداع | Set goodbye channel",
        ]), inline=False)

        embed.set_footer(text="FF Info Bot 🎮 | Prefix: !")
        await ctx.send(embed=embed)

    async def cog_unload(self):
        await self.session.close()

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
