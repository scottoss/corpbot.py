import asyncio, discord
from   Cogs import Nullify

bot = None

def setup(bot_start):
    # This module isn't actually a cog - but it is a place
    # we can call "a trash fire"
    global bot
    bot = bot_start
    return

def suppressed(ctx,msg):
	# Checks if the passed server is suppressing @here and @everyone and adjust the msg accordingly
	guild = ctx if isinstance(ctx,discord.Guild) else ctx.guild if isinstance(ctx,discord.ext.commands.Context) else None
	if not guild: return msg
	settings = bot.get_cog("Settings")
	if not settings: return msg
	return Nullify.clean(msg) if settings.getServerStat(guild, "SuppressMentions", True) else msg

def is_admin(ctx,member=None):
	# Checks if the user in the passed context is admin
	member = ctx.author if not member else member
	return member.permissions_in(ctx.channel).administrator

def is_bot_admin_only(ctx,member=None):
	# Checks only if we're bot admin
	settings = bot.get_cog("Settings")
	if not settings: return False
	member = ctx.author if not member else member
	if not hasattr(member,"roles"): return False # No roles to iterate - can't be bot admin
	return any(role for role in member.roles for check in settings.getServerStat(ctx.guild, "AdminArray", []) if str(role.id) == str(check["ID"]))

def is_bot_admin(ctx,member=None):
	# Checks if the user in the passed context is admin or bot admin
	member = ctx.author if not member else member
	return member.permissions_in(ctx.channel).administrator or is_bot_admin_only(ctx,member)

async def is_admin_reply(ctx,member=None,message="You do not have sufficient privileges to access this command.",message_when=False):
	# Auto-replies if the user doesn't have admin privs
	are_we = is_admin(ctx,member)
	if are_we == message_when: await ctx.send(message)
	return are_we

async def is_bot_admin_only_reply(ctx,member=None,message="You do not have sufficient privileges to access this command.",message_when=False):
	# Auto-replies if the user doesn't have admin or bot admin privs
	are_we = is_bot_admin_only(ctx,member)
	if are_we == message_when: await ctx.send(message)
	return are_we

async def is_bot_admin_reply(ctx,member=None,message="You do not have sufficient privileges to access this command.",message_when=False):
	# Auto-replies if the user doesn't have admin or bot admin privs
	are_we = is_bot_admin(ctx,member)
	if are_we == message_when: await ctx.send(message)
	return are_we

def yes_no_setting(ctx,display_name,setting_name,yes_no=None):
	# Get or set a true/false value and return the resulting message
	guild = ctx if isinstance(ctx,discord.Guild) else ctx.guild if isinstance(ctx,discord.ext.commands.Context) else None
	if not guild: return "I can't get a guild from here :("
	settings = bot.get_cog("Settings")
	if not settings: return "Something is wrong with my settings module :("
	current = settings.getServerStat(guild, setting_name)
	if yes_no == None:
		# Output what we have
		return "{} currently *{}*.".format(display_name,"enabled" if current else "disabled")
	elif yes_no.lower() in [ "yes", "on", "true", "enabled", "enable" ]:
		yes_no = True
		msg = "{} {} *enabled*.".format(display_name,"remains" if current else "is now")
	elif yes_no.lower() in [ "no", "off", "false", "disabled", "disable" ]:
		yes_no = False
		msg = "{} {} *disabled*.".format(display_name,"is now" if current else "remains")
	else:
		msg = "That's not a valid setting."
		yes_no = current
	if not yes_no == current:
		settings.setServerStat(ctx.guild, setting_name, yes_no)
	return msg