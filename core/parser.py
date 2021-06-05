import re
import traceback

import eventlet
from graia.application import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain

from core.loader import Modules, logger_info
from core.template import sendMessage, Nudge
from core.utils import getsetu
from database import BotDB as database


async def parser(kwargs: dict):
    """
    接收消息必经的预处理器
    :param kwargs: 从监听器接收到的dict，该dict将会经过此预处理器传入下游
    :return: 无返回
    """
    if 'TEST' in kwargs:
        display = kwargs['command']
    else:
        display = kwargs[MessageChain].asDisplay()  # 将消息转换为一般显示形式
    if len(display) == 0:  # 转换后若为空消息则停止执行
        return
    command_prefix = ['~', '～']  # 消息前缀
    if Group in kwargs:  # 若为群组
        trigger = kwargs[Member].id
    if Friend in kwargs:  # 若为好友
        trigger = kwargs[Friend].id
    if 'TEST' in kwargs:
        trigger = 0
    if trigger == 1143754816:  # 特殊规则
        display = re.sub('^.*:\n', '', display)
    strip_display_space = display.split(' ')
    display_list = []  # 清除指令中间多余的空格
    for x in strip_display_space:
        if x != '':
            display_list.append(x)
    display = ' '.join(display_list)
    if database.check_black_list(trigger):  # 检查是否在黑名单
        if not database.check_white_list(trigger):  # 检查是否在白名单
            return  # 在黑名单且不在白名单，给我爪巴
    if display.find('色图来') != -1:  # 双倍快乐给我爬
        await getsetu(kwargs)
        return
    if display[0] in command_prefix:  # 检查消息前缀
        logger_info(kwargs)
        command = re.sub(r'^' + display[0], '', display)
        command_list = command.split('&&')  # 并行命令处理
        command_remove_list = ['\n', ' ']  # 首尾需要移除的东西
        for x in command_remove_list:
            command_list_cache = []
            for y in command_list:
                split_list = y.split(x)
                for _ in split_list:
                    if split_list[0] == '':
                        del split_list[0]
                    if len(split_list) > 0:
                        if split_list[-1] == '':
                            del split_list[-1]
                for _ in split_list:
                    if len(split_list) > 0:
                        if split_list[0][0] in command_prefix:
                            split_list[0] = re.sub(r'^' + display[0], '', split_list[0])
                command_list_cache.append(x.join(split_list))
            command_list = command_list_cache
        command_duplicated_list = []  # 移除重复命令
        for x in command_list:
            if x not in command_duplicated_list:
                command_duplicated_list.append(x)
        command_list = command_duplicated_list
        if len(command_list) > 5:
            if not database.check_superuser(kwargs):
                await sendMessage(kwargs, '你不是本机器人的超级管理员，最多只能并排执行5个命令。')
                return
        for command in command_list:
            command_spilt = command.split(' ')  # 切割消息
            try:
                kwargs['trigger_msg'] = command  # 触发该命令的消息，去除消息前缀
                kwargs['bot_modules'] = Modules
                command_first_word = command_spilt[0]
                if command_first_word in Modules['alias']:
                    command_spilt[0] = Modules['alias'][command_first_word]
                    command = ' '.join(command_spilt)
                    command_spilt = command.split(' ')
                    command_first_word = command_spilt[0]
                    kwargs['trigger_msg'] = command
                if command_first_word in Modules['command']:  # 检查触发命令是否在模块列表中
                    if Group in kwargs:
                        await Nudge(kwargs)
                        check_command_enable = database.check_enable_modules(kwargs[Group].id,
                                                                             command_first_word)  # 检查群组是否开启模块
                        if not check_command_enable:  # 若未开启
                            await sendMessage(kwargs, f'此模块未启用，请管理员在群内发送~enable {command_first_word}启用本模块。')
                            return
                    await Modules['command'][command_first_word](kwargs)  # 将dict传入下游模块
                elif command_first_word in Modules['essential']:  # 若触发的对象命令为基础命令
                    if Group in kwargs:
                        await Nudge(kwargs)
                    await Modules['essential'][command_first_word](kwargs)
                elif command_first_word in Modules['admin']:  # 若触发的对象为超管命令
                    if database.check_superuser(kwargs):  # 检查是否为超管
                        await Modules['admin'][command_first_word](kwargs)
                    else:
                        await sendMessage(kwargs, '权限不足')
            except Exception:
                await sendMessage(kwargs, '执行命令时发生错误，请报告管理员：\n' + traceback.format_exc())
    # 正则模块部分
    if Group in kwargs:
        for regex in Modules['regex']:  # 遍历正则模块列表
            check_command_enable = database.check_enable_modules(kwargs[Group].id,
                                                                 regex)  # 检查群组是否打开模块
            if check_command_enable:
                await Modules['regex'][regex](kwargs)  # 将整条dict传入下游正则模块
    if Friend in kwargs:
        for regex in Modules['regex']:
            await Modules['regex'][regex](kwargs)
    return
