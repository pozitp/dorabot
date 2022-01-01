#include <tgbot/tgbot.h>

#include <memory>
#include "spdlog/spdlog.h"
//#include <iostream>
//#include <fstream>
//#include <cstdio>
//#include <cstdlib>
//#include <cmath>
//#include <chrono>

using namespace std;
map <string, function<void()>> commands;
//auto startProc = chrono::steady_clock::now();

int main() {
    spdlog::set_level(spdlog::level::debug);
    TgBot::Bot bot(getenv("TOKEN"));

    vector<TgBot::BotCommand::Ptr> commandsList;

    TgBot::BotCommand::Ptr cmdArray(new TgBot::BotCommand);
    cmdArray->command = "start";
    cmdArray->description = "начать";
    commandsList.push_back(cmdArray);

    cmdArray = std::make_shared<TgBot::BotCommand>();
    cmdArray->command = "help";
    cmdArray->description = "помощь";
    commandsList.push_back(cmdArray);

    cmdArray = std::make_shared<TgBot::BotCommand>();
    cmdArray->command = "stop";
    cmdArray->description = "остановить бота";
    commandsList.push_back(cmdArray);

    bot.getApi().setMyCommands(commandsList);   // set telegram commands list

    bot.getEvents().onCommand("start", [&bot](const TgBot::Message::Ptr& message) {
        bot.getApi().sendAnimation(message->chat->id,
                                   "https://i.imgur.com/87D8gXM.mp4",
                                   0,0,0,"",
                                   "Скоро тут будет *ЧТО НАДО*",
                                   message->messageId,
                                   nullptr,
                                   "markdown",
                                   true);
    });

    bot.getEvents().onAnyMessage([&bot](TgBot::Message::Ptr message) {
        // welcome and goodbye messages
        if (message->newChatMember)
            bot.getApi().sendAnimation(message->chat->id,
                                       "https://i.imgur.com/ISB387m.mp4",
                                       0,0,0,"",
                                       "@" + message->newChatMember->username +
                                       ", well done soldier. Отныне ты в *" +
                                       message->chat->title +
                                       "*. You're welcome!",
                                       message->messageId,
                                       nullptr,
                                       "markdown");
        if (message->leftChatMember)
            bot.getApi().sendAnimation(message->chat->id,
                                       "https://i.imgur.com/87D8gXM.mp4",
                                       0,0,0,"",
                                       "Скоро тут будет *ЧТО НАДО*",
                                       message->messageId,
                                       nullptr,
                                       "markdown");

        if (message->from->id == bot.getApi().getMe()->id) return;  // check if message not from bot

        // set keys and functions for commands
        commands["/help@whitrom_bot"] = [&bot, &message](){
            bot.getApi().sendAnimation(message->chat->id,
                                       "https://i.imgur.com/87D8gXM.mp4",
                                       0,0,0,"",
                                       "Скоро тут будет *ЧТО НАДО*",
                                       message->messageId,
                                       nullptr,
                                       "markdown",
                                       true);
        };
        commands["/stop@whitrom_bot"] = [&bot, &message](){
            try {   // try to kick member
                bot.getApi().kickChatMember(message->chat->id, message->from->id);
                bot.getApi().unbanChatMember(message->chat->id, message->from->id);
                try {
                    bot.getApi().sendMessage(message->from->id, "https://t.me/+Vu2w9gskUeOiNkGW");
                } catch (TgBot::TgException&) {
                    bot.getApi().sendMessage(message->chat->id, "https://t.me/+Vu2w9gskUeOiNkGW");
                }
            } catch (TgBot::TgException& e) {
                bot.getApi().sendMessage(message->chat->id,
                                         "Error:```\n" + string(e.what()) + "```",
                                         false, 0,
                                         nullptr, "markdown");
            }
        };
        string delimiter = " ";
        auto itr = commands.find((message->text).substr(0, (message->text).find(delimiter)));   // split by space
        if (itr != commands.end()) {    // check in map
            (itr->second)();    // run command
        }
    });
    try {   // run bot
        string usernameLog = bot.getApi().getMe()->username;
        spdlog::info("Bot username: " + usernameLog);
        TgBot::TgLongPoll longPoll(bot);
        spdlog::info("Long poll started!");
        while (true) {
            longPoll.start();
        }
    } catch (TgBot::TgException& e) {
        spdlog::error(e.what());
    }
    return 0;
}
