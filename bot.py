import discord
from discord import app_commands
from discord.ext import commands
import traceback
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.presences = True

guild_id = 790828063541559296  # Updated guild ID
channel_id = 1378756844746706975  # Channel ID for sending violation reports
additional_channel_id = 1378657582507491328  # Additional channel ID

def create_log_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Helper function to create consistent log embeds"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    return embed

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

        # Check for "شكرا" message
        if "شكرا" in message.content.lower():
            await message.reply("العفو! دائماً في خدمتك 😊")
            return

        # Check for "مرحبا" message
        if "مرحبا" in message.content.lower():
            await message.reply("مرحباً بك! كيف حالك اليوم?")
            return

        # Check for "استلام" message
        if "استلام" in message.content.lower():
            await message.channel.send(f"**__ تم استلام التكت من قبل الادري {message.author.mention} يرجى عدم تدخل الفريق الادري\n\nتفضل كيف اقدر اخدمك ؟ __**")
            return

        # Check for ".." message
        if ".." in message.content:
            await message.channel.send("https://media.discordapp.net/attachments/1374077173178171422/1374835686791970938/789800330045030401.webp?ex=68322202&is=6830d082&hm=12832bb0a850243ac7052cff9467923493cf8e23413d320943968b771b626884&=&format=webp")
            return

        # Check for specific user mention
        if "<@1307733573549166713>" in message.content:
            await message.reply("اف تبي القادح حموو :smirk_cat: :gloves: خله يرجال لاتنمشه تراه بيقدح عليك يلد")

        # Check for exact word "اسم" followed by space or end of message
        if message.content.lower().startswith('اسم ') or message.content.lower() == 'اسم':
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

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Check for role changes
    if before.roles != after.roles:
        roles_added = [role for role in after.roles if role not in before.roles]
        roles_removed = [role for role in before.roles if role not in after.roles]

        if roles_added:
            added_roles_names = [role.name for role in roles_added]
            embed = create_log_embed(
                "Roles Added",
                f"**User:** {after.name} ({after.id})\n**Roles Added:** {', '.join(added_roles_names)}",
                discord.Color.green()
            )
            role_give_log_general = after.guild.get_channel(1372614055352602844)
            if role_give_log_general:
                await role_give_log_general.send(embed=embed)

        if roles_removed:
            removed_roles_names = [role.name for role in roles_removed]
            embed = create_log_embed(
                "Roles Removed",
                f"**User:** {after.name} ({after.id})\n**Roles Removed:** {', '.join(removed_roles_names)}",
                discord.Color.red()
            )
            role_remove_log_general = after.guild.get_channel(1372614104296194169)
            if role_remove_log_general:
                await role_remove_log_general.send(embed=embed)

    # Check for timeout changes
    if before.timed_out_until != after.timed_out_until:
        timeout_log_channel = after.guild.get_channel(1372613020592766996)
        if timeout_log_channel:
            if after.timed_out_until:
                embed = create_log_embed(
                    "Member Timed Out",
                    f"**User:** {after.name} ({after.id})\n**Timeout Until:** {after.timed_out_until.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                    discord.Color.orange()
                )
                await timeout_log_channel.send(embed=embed)
            else:
                embed = create_log_embed(
                    "Timeout Removed",
                    f"**User:** {after.name} ({after.id})",
                    discord.Color.green()
                )
                await timeout_log_channel.send(embed=embed)

    # Check for nickname changes
    if before.nick != after.nick:
        nickname_log_channel = after.guild.get_channel(1372613922518994965)
        if nickname_log_channel:
            embed = create_log_embed(
                "Nickname Changed",
                f"**User:** {after.name} ({after.id})\n**Before:** {before.nick or before.name}\n**After:** {after.nick or after.name}",
                discord.Color.blue()
            )
            await nickname_log_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
        
    msg_delete_log = message.guild.get_channel(1372613455684829296)
    if not msg_delete_log:
        return

    embed = create_log_embed(
        "Message Deleted",
        f"**Author:** {message.author.name} ({message.author.id})\n**Channel:** {message.channel.mention}\n**Content:** {message.content}",
        discord.Color.red()
    )
    await msg_delete_log.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
        
    if before.content == after.content:
        return

    msg_edit_log = before.guild.get_channel(1372613613130354860)
    if not msg_edit_log:
        return

    embed = create_log_embed(
        "Message Edited",
        f"**Author:** {before.author.name} ({before.author.id})\n**Channel:** {before.channel.mention}\n**Before:** {before.content}\n**After:** {after.content}",
        discord.Color.blue()
    )
    await msg_edit_log.send(embed=embed)

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
    special_role_id = 1351799099384533025
    if not (any(role.id == allowed_role_id for role in interaction.user.roles) or 
            any(role.id == special_role_id for role in interaction.user.roles)):
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
    # Check for Manage Roles permission or special role
    special_role_id = 1351799099384533025
    if not (interaction.user.guild_permissions.manage_roles or 
            any(role.id == special_role_id for role in interaction.user.roles)):
        await interaction.response.send_message('ليس لديك صلاحية ادارة الرتب.', ephemeral=True)
        return
    
    # Check if user is trying to give a role higher than their highest role
    user_highest_role = max(interaction.user.roles, key=lambda r: r.position)
    if role.position >= user_highest_role.position:
        await interaction.response.send_message('لا يمكنك اعطاء رتبة اعلى من رتبتك.', ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    try:
        await member.add_roles(role)
        await interaction.followup.send(f'تم اعطاء الرتبة {role.mention} إلى {member.mention}')
        # Log the action
        role_give_log = interaction.guild.get_channel(1372614055352602844)
        if role_give_log:
            embed = create_log_embed(
                "Role Given (Command)",
                f"**Given By:** {interaction.user.name} ({interaction.user.id})\n**Given To:** {member.name} ({member.id})\n**Role:** {role.name}",
                discord.Color.green()
            )
            await role_give_log.send(embed=embed)
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
    # Check for Manage Roles permission or special role
    special_role_id = 1351799099384533025
    if not (interaction.user.guild_permissions.manage_roles or 
            any(role.id == special_role_id for role in interaction.user.roles)):
        await interaction.response.send_message('ليس لديك صلاحية ادارة الرتب.', ephemeral=False)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        await member.remove_roles(role)
        await interaction.followup.send(f'تم ازالة الرتبة {role.mention} من {member.mention}')
        # Log the action
        role_remove_log = interaction.guild.get_channel(1372614104296194169)
        if role_remove_log:
            embed = create_log_embed(
                "Role Removed (Command)",
                f"**Removed By:** {interaction.user.name} ({interaction.user.id})\n**Removed From:** {member.name} ({member.id})\n**Role:** {role.name}",
                discord.Color.red()
            )
            await role_remove_log.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send('ليس لدي الصلاحية لازالة هذه الرتبة.')
    except Exception as e:
        await interaction.followup.send(f'حدث خطأ غير متوقع: {e}')

@bot.command(name="اسم")
@commands.has_permissions(manage_nicknames=True)
async def set_nickname(ctx, member: discord.Member, *, new_nickname: str):
    # Check for Manage Nicknames permission or special role
    special_role_id = 1351799099384533025
    if not (ctx.author.guild_permissions.manage_nicknames or 
            any(role.id == special_role_id for role in ctx.author.roles)):
        await ctx.send('ليس لديك صلاحية تغيير الأسماء.')
        return

    # Check if user is trying to change nickname of someone with higher role
    user_highest_role = max(ctx.author.roles, key=lambda r: r.position)
    target_highest_role = max(member.roles, key=lambda r: r.position)
    
    if target_highest_role.position >= user_highest_role.position:
        await ctx.send('لا يمكنك تغيير اسم شخص لديه رتبة اعلى منك.')
        return

    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f'تم تغيير اسم {member.mention} إلى {new_nickname}')
        # Log the action
        nickname_log_channel = ctx.guild.get_channel(1372613922518994965)
        if nickname_log_channel:
            embed = create_log_embed(
                "Nickname Changed (Command)",
                f"**Changed By:** {ctx.author.name} ({ctx.author.id})\n**User:** {member.name} ({member.id})\n**Before:** {member.nick or member.name}\n**After:** {new_nickname}",
                discord.Color.blue()
            )
            await nickname_log_channel.send(embed=embed)
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

@bot.tree.command(name="timeout", description="توقيف عضو مؤقتاً", guild=discord.Object(id=guild_id))
@app_commands.describe(
    العضو="العضو المراد توقيفه",
    المدة="مدة التوقيف (مثال: 1h, 30m, 1d)"
)
async def timeout(interaction: discord.Interaction, العضو: discord.Member, المدة: str):
    # Check for Timeout Members permission or special role
    special_role_id = 1351799099384533025
    if not (interaction.user.guild_permissions.moderate_members or 
            any(role.id == special_role_id for role in interaction.user.roles)):
        await interaction.response.send_message('ليس لديك صلاحية توقيف الأعضاء.', ephemeral=True)
        return

    try:
        duration = 0
        if المدة.endswith('s'):
            duration = int(المدة[:-1])
        elif المدة.endswith('m'):
            duration = int(المدة[:-1]) * 60
        elif المدة.endswith('h'):
            duration = int(المدة[:-1]) * 3600
        elif المدة.endswith('d'):
            duration = int(المدة[:-1]) * 86400
        else:
            await interaction.response.send_message('صيغة المدة غير صحيحة. استخدم s, m, h, أو d (مثال: 1h, 30m, 1d)', ephemeral=True)
            return

        if duration > 2419200:
            await interaction.response.send_message('لا يمكن توقيف عضو لأكثر من 28 يوم.', ephemeral=True)
            return

        await العضو.timeout(datetime.timedelta(seconds=duration), reason=f"Timeout by {interaction.user}")
        await interaction.response.send_message(f'تم توقيف {العضو.mention} لمدة {المدة}', ephemeral=False)
        
        timeout_log_channel = interaction.guild.get_channel(1372613020592766996)
        if timeout_log_channel:
            embed = create_log_embed(
                "Member Timed Out (Command)",
                f"**Timed Out By:** {interaction.user.name} ({interaction.user.id})\n**User:** {العضو.name} ({العضو.id})\n**Duration:** {المدة}",
                discord.Color.orange()
            )
            await timeout_log_channel.send(embed=embed)
    except ValueError:
        await interaction.response.send_message('صيغة المدة غير صحيحة. استخدم أرقام فقط (مثال: 1h, 30m, 1d)', ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message('ليس لدي الصلاحية لتوقيف هذا العضو.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'حدث خطأ غير متوقع: {e}', ephemeral=True)

@bot.tree.command(name="ban", description="حظر عضو", guild=discord.Object(id=guild_id))
@app_commands.describe(
    العضو="العضو المراد حظره",
    السبب="سبب الحظر (اختياري)"
)
async def ban(interaction: discord.Interaction, العضو: discord.Member, السبب: str = None):
    # Check for Ban Members permission or special role
    special_role_id = 1351799099384533025
    if not (interaction.user.guild_permissions.ban_members or 
            any(role.id == special_role_id for role in interaction.user.roles)):
        await interaction.response.send_message('ليس لديك صلاحية حظر الأعضاء.', ephemeral=True)
        return

    user_highest_role = max(interaction.user.roles, key=lambda r: r.position)
    target_highest_role = max(العضو.roles, key=lambda r: r.position)
    
    if target_highest_role.position >= user_highest_role.position:
        await interaction.response.send_message('لا يمكنك حظر شخص لديه رتبة اعلى منك.', ephemeral=True)
        return

    try:
        ban_reason = f"Banned by {interaction.user}"
        if السبب:
            ban_reason += f" | Reason: {السبب}"

        await العضو.ban(reason=ban_reason)
        
        if السبب:
            await interaction.response.send_message(f'تم حظر {العضو.mention}\nالسبب: {السبب}', ephemeral=False)
        else:
            await interaction.response.send_message(f'تم حظر {العضو.mention}', ephemeral=False)
        
        ban_log_channel = interaction.guild.get_channel(1349964174075232276)
        if ban_log_channel:
            embed = create_log_embed(
                "Member Banned (Command)",
                f"**Banned By:** {interaction.user.name} ({interaction.user.id})\n**User:** {العضو.name} ({العضو.id})\n**Reason:** {السبب if السبب else 'No reason provided'}",
                discord.Color.dark_red()
            )
            await ban_log_channel.send(embed=embed)
            
    except discord.Forbidden:
        await interaction.response.send_message('ليس لدي الصلاحية لحظر هذا العضو.', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'حدث خطأ غير متوقع: {e}', ephemeral=True)

@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    ban_log_channel = guild.get_channel(1349964174075232276)
    
    if ban_log_channel:
        embed = create_log_embed(
            "Member Banned",
            f"**User:** {user.name} ({user.id})",
            discord.Color.dark_red()
        )
        await ban_log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    channel_create_log = channel.guild.get_channel(1372613128214282340)
    if not channel_create_log:
        return

    embed = create_log_embed(
        "Channel Created",
        f"**Channel:** {channel.mention}\n**Type:** {channel.type}\n**Category:** {channel.category.name if channel.category else 'None'}",
        discord.Color.green()
    )
    await channel_create_log.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    channel_delete_log = channel.guild.get_channel(1372613339414401044)
    if not channel_delete_log:
        return

    embed = create_log_embed(
        "Channel Deleted",
        f"**Channel Name:** {channel.name}\n**Type:** {channel.type}\n**Category:** {channel.category.name if channel.category else 'None'}",
        discord.Color.red()
    )
    await channel_delete_log.send(embed=embed)

@bot.event
async def on_guild_channel_update(before, after):
    channel_edit_log = before.guild.get_channel(1372614348907741344)
    if not channel_edit_log:
        return

    changes = []
    if before.name != after.name:
        changes.append(f"**Name:** {before.name} → {after.name}")
    if before.category != after.category:
        changes.append(f"**Category:** {before.category.name if before.category else 'None'} → {after.category.name if after.category else 'None'}")
    if before.position != after.position:
        changes.append(f"**Position:** {before.position} → {after.position}")

    if changes:
        embed = create_log_embed(
            "Channel Updated",
            f"**Channel:** {after.mention}\n" + "\n".join(changes),
            discord.Color.blue()
        )
        await channel_edit_log.send(embed=embed)

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