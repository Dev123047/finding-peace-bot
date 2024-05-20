import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)
guild_id = os.getenv('GUILD_ID', 1110509419080458240)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await bot.tree.sync()
    print(synced)

@bot.event
async def on_member_join(member: discord.Member):
    nick1 = member.display_name+" > 0"
    await member.edit(nick=nick1)

@bot.tree.command()
async def solve(interaction: discord.Interaction, answer: str, explanation: str):
    end = 9 #end level here
    guild = interaction.client.get_guild(guild_id)
    member = guild.get_member(interaction.user.id)
    target_channel = discord.utils.get(guild.channels,name="solve-requests")
    current_level = member.nick.split(">")[-1]
    embed = discord.Embed(title="Solve Request")
    embed.set_author(name=interaction.user.display_name)
    embed.add_field(name="Username",value=interaction.user.id,inline=False)
    embed.add_field(name="Current Level",value=current_level,inline=False)
    embed.add_field(name="Provided Answer",value=answer,inline=False)
    embed.add_field(name="Explanation Given",value=explanation,inline=False)

    approve = discord.ui.Button(style=discord.ButtonStyle.green,label="Approve")
    reject = discord.ui.Button(style=discord.ButtonStyle.red,label="Reject")
    question = discord.ui.Button(style=discord.ButtonStyle.blurple,label="Question")
    async def approve_callback(interaction2: discord.Interaction):
        user_id = embed.fields[0].value
        embed_approve_confirm = discord.Embed(title='Confirmation for APPROVAL of a request')
        embed_approve_confirm.add_field(name="Username",value=interaction.user.display_name)
        confirm = discord.ui.Button(style=discord.ButtonStyle.green,label="Confirm Accept!")
        cancel = discord.ui.Button(style=discord.ButtonStyle.gray,label="Cancel")
        async def confirmation_approve_callback(interaction3: discord.Interaction):
            guild = interaction3.client.get_guild(guild_id)
            member = guild.get_member(int(user_id))
            x = member.nick.split(">")
            if (x[-1] == 0):
                await member.add_roles(discord.utils.get(guild.roles,name="1"))
            elif (int(x[-1].strip()) == end):
                await member.remove_roles(discord.utils.get(guild.roles,name=str(x[-1]).strip()))
                x[-1] = str(int(x[-1].strip())+1)
                await member.add_roles(discord.utils.get(guild.roles,name="Complete"))
                nickname1 = x[0]+' ⭐'
                await member.edit(nick=nickname1)
            else:
                await member.remove_roles(discord.utils.get(guild.roles,name=str(x[-1]).strip()))
                x[-1] = str(int(x[-1].strip())+1)
                await member.add_roles(discord.utils.get(guild.roles,name=str(x[-1]).strip()))
                nickname1 = x[0]+' > '+x[-1]
                await member.edit(nick=nickname1)
            await member.send('You have successfully solved '+str(int(x[-1].strip())-1))
        await interaction2.response.send_message("Confirmation for APPROVE sent!")
        async def cancel_approve(interaction3: discord.Interaction):
            await interaction3.response.send_message('Approve request cancelled!')
        confirm.callback = confirmation_approve_callback
        cancel.callback = cancel_approve
        view2 = discord.ui.View(timeout=None)
        view2.add_item(confirm)
        view2.add_item(cancel)
        await target_channel.send(embed=embed_approve_confirm,view=view2)
    async def reject_callback(interaction2: discord.Interaction):
        embed_deny_confirm = discord.Embed(title='Confirmation for DENIAL of a request')
        embed_deny_confirm.add_field(name="Username",value=interaction.user.display_name)
        deny = discord.ui.Button(style=discord.ButtonStyle.red,label="Confirm Deny!")
        cancel = discord.ui.Button(style=discord.ButtonStyle.gray,label="Cancel")
        async def confirmation_deny_callback(interaction3: discord.Interaction):
            await member.send('Your answer has been denied, try again')
            await interaction3.response.send_message('Solve request rejected!')
        async def cancel_approve(interaction3: discord.Interaction):
            await interaction3.response.send_message('Deny request cancelled!')
        deny.callback = confirmation_deny_callback
        cancel.callback = cancel_approve
        view2 = discord.ui.View(timeout=None)
        view2.add_item(deny)
        view2.add_item(cancel)
        await target_channel.send(embed=embed_deny_confirm,view=view2)
        await interaction2.response.send_message("Confirmation for DENY sent!")
    async def question_callback(interaction2):
        await member.send('Please clarify your answer by sending another submission')
        await interaction2.response.send_message('Solve request questioned!')
    approve.callback = approve_callback
    reject.callback = reject_callback
    question.callback = question_callback
    view = discord.ui.View(timeout=None)
    view.add_item(approve)
    view.add_item(reject)
    view.add_item(question)
    await target_channel.send(embed=embed,view=view)
    await interaction.response.send_message('Request Sent!')

@bot.tree.command()
async def setlevel(interaction: discord.Interaction, user: discord.User, level: str):
    end = 9 #end level here
    guild = interaction.client.get_guild(guild_id)
    target_channel = discord.utils.get(guild.channels,name="solve-requests")
    embed = discord.Embed(title='Confirm set level')
    embed.set_author(name=interaction.user.display_name)
    embed.add_field(name="Username",value=user.display_name)
    embed.add_field(name="Current Level", value=user.display_name.split(">")[-1].strip())
    embed.add_field(name="New Level", value=level.strip())
    confirm = discord.ui.Button(style=discord.ButtonStyle.green,label="Confirm")
    cancel = discord.ui.Button(style=discord.ButtonStyle.red,label="Cancel")
    async def confirm_callback(interaction2: discord.Interaction):
        member = guild.get_member(user.id)
        x = member.nick.split(">")
        if int(level.strip()) <= end:
            if (x[-1] == 0):
                await member.add_roles(discord.utils.get(guild.roles,name=level.strip()))
                await interaction2.response.send_message('User level changed!')
            elif x[0][-1] == "⭐":
                current = x[0][0:-1]+"> "+level
                await member.edit(nick=current)
                await member.remove_roles(discord.utils.get(guild.roles,name="Complete"))
                await member.add_roles(discord.utils.get(guild.roles,name=level.strip()))
                await interaction2.response.send_message('User level changed!')
            else:
                await member.remove_roles(discord.utils.get(guild.roles,name=str(x[-1]).strip()))
                await member.add_roles(discord.utils.get(guild.roles,name=level.strip()))
                nickname1 = x[0]+' > '+level.strip()
                await member.edit(nick=nickname1)
                await interaction2.response.send_message('User level changed!')
        else:
            await interaction2.response.send_message('The input level is exceeding the end level!')
    async def cancel_callback(interaction2: discord.Interaction):
        await interaction2.response.send_message('Set level command cancelled!')
    confirm.callback = confirm_callback
    cancel.callback = cancel_callback
    view = discord.ui.View(timeout=None)
    view.add_item(confirm)
    view.add_item(cancel)
    await target_channel.send(embed=embed,view=view)
    await interaction.response.send_message("Confirmation sent!")

bot.run(os.getenv('BOT_TOKEN'))
