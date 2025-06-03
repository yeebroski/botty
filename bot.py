import discord
from discord import app_commands
from discord.ext import commands
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

guild_id = 790828063541559296  # Updated guild ID
channel_id = 1378756844746706975  # Channel ID for sending violation reports
additional_channel_id = 1378657582507491328  # Additional channel ID

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.synced = False

    async def setup_hook(self):
        print(f"Syncing commands to guild {guild_id}")
        guild = discord.Object(id=guild_id)
        # Clear commands for this specific guild (optional, but good for development)
        # self.tree.clear_commands(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"Synced commands to guild {guild.id} successfully!")
        self.synced = True

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.lower().startswith('اسم'):
            # Split the message content
            parts = message.content.split()
            if len(parts) < 3:
                await message.channel.send('الاستخدام الصحيح: اسم @العضو الاسم_الجديد')
                return

            # Check for Manage Nicknames permission
            if not message.author.guild_permissions.manage_nicknames:
                await message.channel.send('ليس لديك صلاحية تغيير الأسماء.')
                return

            # Get the member mention
            try:
                member = message.mentions[0]
            except IndexError:
                await message.channel.send('الرجاء منشن العضو المراد تغيير اسمه.')
                return

            # Get the new nickname (everything after the mention)
            new_nickname = ' '.join(parts[2:])

            try:
                await member.edit(nick=new_nickname)
                await message.channel.send(f'تم تغيير اسم {member.mention} إلى {new_nickname}')
            except discord.Forbidden:
                await message.channel.send('ليس لدي الصلاحية لتغيير الاسم.')
            except Exception as e:
                await message.channel.send(f'حدث خطأ غير متوقع: {e}')

        await self.process_commands(message)

bot = MyBot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Define the 'role' command group
role_group = app_commands.Group(name="role", description="Commands related to roles")
bot.tree.add_command(role_group, guild=discord.Object(id=guild_id))

@bot.tree.command(name="رصد", description="رصد مخالفة", guild=discord.Object(id=guild_id))
@app_commands.describe(
    منشن="منشن المخالف",
    القيمة="قيمة المخالفة",
    السبب="سبب المخالفة",
    حاله_الدفع="تم السداد (أي نص)"
)
async def rasad(interaction: discord.Interaction, منشن: discord.Member, القيمة: str, السبب: str, حاله_الدفع: str):
    # Role restriction
    allowed_role_id = 1368378789301714964
    if not any(role.id == allowed_role_id for role in interaction.user.roles):
        await interaction.response.send_message('ليس لديك الصلاحية لاستخدام هذا الأمر.', ephemeral=True)
        return
    channel = bot.get_channel(channel_id)
    additional_channel = bot.get_channel(additional_channel_id)
    if channel or additional_channel:
        embed_message = (
            '**``` رصد مخالفة ```**\n\n'
            f'اسمك : {interaction.user.mention}\n\n'
            f'منشن المخالف : {منشن.mention}\n\n'
            f'قيمة المخالفه : {القيمة} \n\n'
            f'سبب المخالفة : {السبب}\n\n'
            'دليل المخالفة :  \n\n'
            f'تم السداد ` {حاله_الدفع} ` : \n\n'
            '``` عدم الالتزام بالنموذج يؤدي الى تحذير ```'
        )
        if channel:
            await channel.send(embed_message)
        if additional_channel:
            await additional_channel.send(embed_message)
        await interaction.response.send_message('تم إرسال المخالفة!', ephemeral=True)
    else:
        await interaction.response.send_message('لم أتمكن من العثور على القناة المطلوبة.', ephemeral=True)

@role_group.command(name="give", description="اعطاء رتبة لعضو")
@app_commands.describe(
    member="العضو",
    role="الرتبة"
)
async def give(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # Check for Manage Roles permission
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message('ليس لديك صلاحية ادارة الرتب.', ephemeral=True)
        return
    
    # Check if user is trying to give a role higher than their highest role
    user_highest_role = max(interaction.user.roles, key=lambda r: r.position)
    if role.position >= user_highest_role.position:
        await interaction.response.send_message('لا يمكنك اعطاء رتبة اعلى من رتبتك.', ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)  # Changed to False to make it public

    try:
        await member.add_roles(role)
        await interaction.followup.send(f'تم اعطاء الرتبة {role.mention} إلى {member.mention}')
    except discord.Forbidden:
        await interaction.followup.send('ليس لدي الصلاحية لاعطاء هذه الرتبة.')
    except Exception as e:
        await interaction.followup.send(f'حدث خطأ غير متوقع: {e}')

@role_group.command(name="remove", description="ازالة رتبة من عضو")
@app_commands.describe(
    member="العضو",
    role="الرتبة"
)
async def remove(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # Check for Manage Roles permission
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message('ليس لديك صلاحية ادارة الرتب.', ephemeral=False)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        await member.remove_roles(role)
        # Keep followup public as originally intended after successful op
        await interaction.followup.send(f'تم ازالة الرتبة {role.mention} من {member.mention}')
    except discord.Forbidden:
        await interaction.followup.send('ليس لدي الصلاحية لازالة هذه الرتبة.')
    except Exception as e:
        await interaction.followup.send(f'حدث خطأ غير متوقع: {e}')

@bot.command(name="اسم")
@commands.has_permissions(manage_nicknames=True)
async def set_nickname(ctx, member: discord.Member, *, new_nickname: str):
    # Check if user is trying to change nickname of someone with higher role
    user_highest_role = max(ctx.author.roles, key=lambda r: r.position)
    target_highest_role = max(member.roles, key=lambda r: r.position)
    
    if target_highest_role.position >= user_highest_role.position:
        await ctx.send('لا يمكنك تغيير اسم شخص لديه رتبة اعلى منك.')
        return

    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f'تم تغيير اسم {member.mention} إلى {new_nickname}')
    except discord.Forbidden:
        await ctx.send('ليس لدي الصلاحية لتغيير الاسم.')
    except Exception as e:
        await ctx.send(f'حدث خطأ غير متوقع: {e}')

@set_nickname.error
async def set_nickname_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('ليس لديك صلاحية تغيير الأسماء.')
    else:
        await ctx.send(f'حدث خطأ غير متوقع: {error}')

# Get token from environment variable
token = os.getenv('DISCORD_TOKEN')
if not token:
    print("Please set the DISCORD_TOKEN environment variable")
    exit(1)

try:
    bot.run(token)
except Exception as e:
    print('An error occurred while running the bot:')
    traceback.print_exc() 