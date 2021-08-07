import asyncio
from enum import auto
import os
import traceback
import json

from core.scheduler import Scheduler
from core.logger import Logger
from core.utils import get_url
from core.loader.decorator import command
from database import BotDBUtil


def getfileversions(path):
    if not os.path.exists(path):
        a = open(path, 'a')
        a.close()
    w = open(path, 'r+')
    s = w.read().split('\n')
    w.close()
    return s


@command('mcv_rss', autorun=True)
@command('mcv_jira_rss', autorun=True)
async def mcv_rss(bot):
    print(111)

    @Scheduler.scheduled_job('interval', seconds=30)
    async def java_main():
        print(111)
        url = 'http://launchermeta.mojang.com/mc/game/version_manifest.json'
        try:
            version_file = os.path.abspath('./assets/mcversion.txt')
            Logger.info('Checking mcv...')
            verlist = getfileversions(version_file)
            file = json.loads(await get_url(url))
            release = file['latest']['release']
            snapshot = file['latest']['snapshot']
            if release not in verlist:
                Logger.info(f'huh, we find {release}.')
                get_target_id = BotDBUtil.Module.get_enabled_this('mcv_rss')
                for x in get_target_id:
                    fetch = bot.fetch_target(x)
                    if fetch:
                        try:
                            await fetch.sendMessage('启动器已更新' + file['latest']['release'] + '正式版。')
                            await asyncio.sleep(0.5)
                        except Exception:
                            traceback.print_exc()
                addversion = open(version_file, 'a')
                addversion.write('\n' + release)
                addversion.close()
                verlist = getfileversions(version_file)
            if snapshot not in verlist:
                Logger.info(f'huh, we find {snapshot}.')
                get_target_id = BotDBUtil.Module.get_enabled_this('mcv_rss')
                for x in get_target_id:
                    fetch = bot.fetch_target(x)
                    if fetch:
                        try:
                            await fetch.sendMessage('启动器已更新' + file['latest']['snapshot'] + '快照。')
                            await asyncio.sleep(0.5)
                        except Exception:
                            traceback.print_exc()
                addversion = open('./assets/mcversion.txt', 'a')
                addversion.write('\n' + snapshot)
                addversion.close()
            Logger.info('mcv checked.')
        except Exception:
            traceback.print_exc()

        @Scheduler.scheduled_job('interval', seconds=30)
        async def java_jira():
            url = 'https://bugs.mojang.com/rest/api/2/project/10400/versions'
            try:
                version_file = os.path.abspath('./assets/mcversion_jira.txt')
                Logger.info('Checking Jira mcv...')
                verlist = getfileversions(version_file)
                file = json.loads(await get_url(url))
                release = []
                for v in file:
                    if not v['archived']:
                        release.append(v['name'])
                for x in release:
                    if x not in verlist:
                        Logger.info(f'huh, we find {x}.')
                        get_target_id = BotDBUtil.Module.get_enabled_this('mcv_jira_rss')
                        for x in get_target_id:
                            fetch = bot.fetch_target(x)
                            if fetch:
                                try:
                                    await fetch.sendMessage('Jira已更新Java版' + file['latest']['snapshot'] + '。\n（Jira上的信息仅作版本号预览用，不代表启动器已更新此版本）')
                                    await asyncio.sleep(0.5)
                                except Exception:
                                    traceback.print_exc()
                        addversion = open(version_file, 'a')
                        addversion.write('\n' + x)
                        addversion.close()
                Logger.info('jira mcv checked.')
            except Exception:
                traceback.print_exc()

        @Scheduler.scheduled_job('interval', seconds=30)
        async def bedrock_jira():
            url = 'https://bugs.mojang.com/rest/api/2/project/10200/versions'
            try:
                version_file = os.path.abspath('./assets/mcversion_jira-bedrock.txt')
                Logger.info('Checking Jira mcv-bedrock...')
                verlist = getfileversions(version_file)
                file = json.loads(await get_url(url))
                release = []
                for v in file:
                    if not v['archived']:
                        release.append(v['name'])
                for x in release:
                    if x not in verlist:
                        Logger.info(f'huh, we find {x}.')
                        get_target_id = BotDBUtil.Module.get_enabled_this('mcv_jira_rss')
                        for x in get_target_id:
                            fetch = bot.fetch_target(x)
                            if fetch:
                                try:
                                    await fetch.sendMessage('Jira已更新基岩版' + file['latest']['snapshot'] + '。\n（Jira上的信息仅作版本号预览用，不代表启动器已更新此版本）')
                                    await asyncio.sleep(0.5)
                                except Exception:
                                    traceback.print_exc()
                        addversion = open(version_file, 'a')
                        addversion.write('\n' + x)
                        addversion.close()
                Logger.info('jira mcv-bedrock checked.')
            except Exception:
                traceback.print_exc()


        @Scheduler.scheduled_job('interval', seconds=30)
        async def bedrock_dungeons():
            url = 'https://bugs.mojang.com/rest/api/2/project/11901/versions'
            try:
                version_file = os.path.abspath('./assets/mcversion_jira-dungeons.txt')
                Logger.info('Checking Jira mcv-bedrock...')
                verlist = getfileversions(version_file)
                file = json.loads(await get_url(url))
                release = []
                for v in file:
                    if not v['archived']:
                        release.append(v['name'])
                for x in release:
                    if x not in verlist:
                        Logger.info(f'huh, we find {x}.')
                        get_target_id = BotDBUtil.Module.get_enabled_this('mcv_jira_rss')
                        for x in get_target_id:
                            fetch = bot.fetch_target(x)
                            if fetch:
                                try:
                                    await fetch.sendMessage('Jira已更新Dungeons ' + file['latest']['snapshot'] + '。\n（Jira上的信息仅作版本号预览用，不代表商店已更新此版本）')
                                    await asyncio.sleep(0.5)
                                except Exception:
                                    traceback.print_exc()
                        addversion = open(version_file, 'a')
                        addversion.write('\n' + x)
                        addversion.close()
                Logger.info('jira mcv-dungeons checked.')
            except Exception:
                traceback.print_exc()
