import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def error_embed(self, msg):
        e = discord.Embed(color=0xFF0000)
        e.description = msg
        return e

    def success_embed(self, msg):
        e = discord.Embed(color=0x00FF7F)
        e.description = msg
        return e

    # =====================
    # !kick
    # =====================
    @commands.hybrid_command(name="kick", description="👢 طرد عضو | Kick a member")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(member="العضو | Member", reason="السبب | Reason")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "لا يوجد سبب | No reason"):
        if member == ctx.author:
            return await ctx.send(embed=self.error_embed("❌ ما تقدر تطرد نفسك! | You can't kick yourself!"))
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.error_embed("❌ ما تقدر تطرد شخص رتبته أعلى منك! | Can't kick higher role!"))

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(title="👢 تم الطرد | Kicked", color=0xFFA500, timestamp=datetime.now())
            embed.add_field(name="👤 العضو | Member", value=str(member), inline=True)
            embed.add_field(name="👮 من | By", value=str(ctx.author), inline=True)
            embed.add_field(name="📝 السبب | Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("❌ ما عندي صلاحية | No permission"))

    # =====================
    # !ban
    # =====================
    @commands.hybrid_command(name="ban", description="🔨 حظر عضو | Ban a member")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="العضو | Member", reason="السبب | Reason")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "لا يوجد سبب | No reason"):
        if member == ctx.author:
            return await ctx.send(embed=self.error_embed("❌ ما تقدر تحظر نفسك! | You can't ban yourself!"))
        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=self.error_embed("❌ ما تقدر تحظر شخص رتبته أعلى منك! | Can't ban higher role!"))

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="🔨 تم الحظر | Banned", color=0xFF0000, timestamp=datetime.now())
            embed.add_field(name="👤 العضو | Member", value=str(member), inline=True)
            embed.add_field(name="👮 من | By", value=str(ctx.author), inline=True)
            embed.add_field(name="📝 السبب | Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("❌ ما عندي صلاحية | No permission"))

    # =====================
    # !unban
    # =====================
    @commands.hybrid_command(name="unban", description="✅ رفع الحظر | Unban a member")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(user_id="ID العضو | Member ID")
    async def unban(self, ctx: commands.Context, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await ctx.guild.unban(user)
            embed = discord.Embed(title="✅ تم رفع الحظر | Unbanned", color=0x00FF7F, timestamp=datetime.now())
            embed.add_field(name="👤 العضو | Member", value=str(user), inline=True)
            embed.add_field(name="👮 من | By", value=str(ctx.author), inline=True)
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send(embed=self.error_embed("❌ المستخدم غير موجود | User not found"))
        except discord.Forbidden:
            await ctx.send(embed=self.error_embed("❌ ما عندي صلاحية | No permission"))

    # =====================
    # !clear
    # =====================
    @commands.hybrid_command(name="clear", description="🗑️ حذف رسائل | Clear messages")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(amount="عدد الرسائل | Number of messages")
    async def clear(self, ctx: commands.Context, amount: int = 10):
        if amount < 1 or amount > 100:
            return await ctx.send(embed=self.error_embed("❌ الرقم يجب بين 1-100 | Number must be 1-100"))

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(embed=self.success_embed(f"🗑️ تم حذف {len(deleted)} رسالة | Deleted {len(deleted)} messages"))
        await msg.delete(delay=3)

    # =====================
    # !mute
    # =====================
    @commands.hybrid_command(name="mute", description="🔇 كتم عضو | Mute a member")
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(member="العضو | Member", reason="السبب | Reason")
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = "لا يوجد سبب | No reason"):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)

        if mute_role in member.roles:
            return await ctx.send(embed=self.error_embed("❌ العضو مكتوم بالفعل | Member already muted"))

        await member.add_roles(mute_role, reason=reason)
        embed = discord.Embed(title="🔇 تم الكتم | Muted", color=0xFFA500, timestamp=datetime.now())
        embed.add_field(name="👤 العضو | Member", value=str(member), inline=True)
        embed.add_field(name="👮 من | By", value=str(ctx.author), inline=True)
        embed.add_field(name="📝 السبب | Reason", value=reason, inline=False)
        await ctx.send(embed=embed)

    # =====================
    # !unmute
    # =====================
    @commands.hybrid_command(name="unmute", description="🔊 رفع الكتم | Unmute a member")
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(member="العضو | Member")
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not mute_role or mute_role not in member.roles:
            return await ctx.send(embed=self.error_embed("❌ العضو ليس مكتوماً | Member is not muted"))

        await member.remove_roles(mute_role)
        embed = discord.Embed(title="🔊 تم رفع الكتم | Unmuted", color=0x00FF7F, timestamp=datetime.now())
        embed.add_field(name="👤 العضو | Member", value=str(member), inline=True)
        embed.add_field(name="👮 من | By", value=str(ctx.author), inline=True)
        await ctx.send(embed=embed)

    # =====================
    # Error Handlers
    # =====================
    @kick.error
    @ban.error
    @unban.error
    @clear.error
    @mute.error
    @unmute.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=self.error_embed("❌ ما عندك صلاحية | You don't have permission"))
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=self.error_embed("❌ العضو غير موجود | Member not found"))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
