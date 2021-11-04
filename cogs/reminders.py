import discord
from discord.ext import commands, tasks
import datetime
from datetime import timedelta


class Reminders(commands.Cog, name="Reminders"):
    def __init__(self, bot):
        self.bot = bot
        self.reminders_collections = bot.database['reminders']
        self.reminder_list = []
        self.get_reminders.start()
        self.check_reminders.start()

    @tasks.loop(count=1)
    async def get_reminders(self):
        reminders = await self.reminders_collections.find().to_list(length=None)
        for reminder in reminders:
            self.reminder_list.append(reminder)

    @tasks.loop(seconds=1)
    async def check_reminders(self):
        for reminder in self.reminder_list:
            now = datetime.datetime.now()
            remind_time = datetime.datetime.fromisoformat(reminder["remindtime"])
            time_comparison = now - remind_time
            if time_comparison >= timedelta(0):
                channel = self.bot.get_channel(int(reminder['channel']))  # gets channel
                await channel.send(reminder["message"])
                if int(reminder["count"]) == 1:
                    await self.reminders_collections.delete_many(reminder)
                    self.reminder_list.remove(reminder)
                elif int(reminder["count"]) != 0:
                    await self.reminders_collections.update_one({"_id": reminder["_id"]}, {"$set": {"count": int(reminder["count"]) - 1}})

    @commands.command()
    async def remindme(self, ctx, time: float, count, *, message):
        now = datetime.datetime.now()
        remindAt = now + timedelta(hours=time)

        highest_id = 0
        for reminder in self.reminder_list:
            if reminder["_id"] > highest_id:
                highest_id = reminder["_id"]

        remind_dict = {"_id": highest_id + 1, "remindtime": remindAt.isoformat(), "count": count, "message": message, "channel": ctx.channel.id}

        await self.reminders_collections.insert_one(remind_dict)
        self.reminder_list.append(remind_dict)
        await ctx.send("reminder set!")


def setup(bot):
    bot.add_cog(Reminders(bot))
