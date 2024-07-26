import heapq
import io
from typing import Annotated, Callable

import discord
from discord.ext import commands
from pydantic_core import PydanticCustomError, ValidationError
from rich.console import Console

from am4.utils.aircraft import Aircraft
from am4.utils.airport import Airport
from am4.utils.db.utils import jaro_winkler_distance

from ..config import cfg
from .channels import channels

COLOUR_ERROR = discord.Colour(0xCA7575)
Suggestions = list[tuple[Annotated[str, "displayed value in command sugg"], Annotated[str, "full description"]]]


class AircraftNotFoundError(commands.BadArgument):
    def __init__(self, acsr: Aircraft.SearchResult):
        super().__init__("Aircraft not found!")
        self.acsr = acsr


class AirportNotFoundError(commands.BadArgument):
    def __init__(self, apsr: Airport.SearchResult):
        super().__init__("Airport not found!")
        self.apsr = apsr


class ValidationErrorBase(commands.BadArgument):
    def __init__(self, err: ValidationError | PydanticCustomError):
        super().__init__()
        self.err = err
        if isinstance(err, ValidationError):
            self.msg = "\n".join(f'`{",".join(e["loc"])}`: {e["msg"]}' for e in err.errors())
        elif isinstance(err, PydanticCustomError):
            self.msg = err.message()
        else:
            self.msg = ""


class SettingValueValidationError(ValidationErrorBase):
    pass


class TPDValidationError(ValidationErrorBase):
    pass


class CfgAlgValidationError(ValidationErrorBase):
    pass


class ConstraintValidationError(ValidationErrorBase):
    pass


class PriceValidationError(ValidationErrorBase):
    pass


class UserBannedError(commands.BadArgument):
    pass


class OutsideMainServerError(commands.CheckFailure):
    pass


class CustomErrHandler:
    def __init__(
        self, ctx: commands.Context, error: commands.CommandError = commands.CommandError(), cmd: str | None = None
    ):
        self.ctx = ctx
        self.error = error
        self.cmd = cmd
        self.handled = False

    @property
    def err_tb(self) -> str:
        v = self.ctx.view
        highlight = " ▔▔▔?" if (wordlen := v.index - v.previous) < 1 else ("▔" * wordlen + "↖")
        return f"```php\n{v.buffer}\n{' ' * v.previous}{highlight}\n```"

    async def raise_for_unhandled(self):
        # we need to set/getattr because @cmd.error and @global.error both catches,
        # we don't want to send the error twice
        if not self.handled and not getattr(self.error, "__handled__", False):
            await self.ctx.send(
                embed=discord.Embed(
                    title="An error occurred!",
                    description=(
                        "Oops! Something real bad happened and I don't know how to handle it.\n"
                        "This incident has been reported to our developers."
                    ),
                    colour=COLOUR_ERROR,
                )
            )
            buf = io.StringIO()
            console = Console(file=buf)
            if self.error is not None:
                console.print_exception(show_locals=True, max_frames=0)

            # inspect(self.ctx, console=console)
            buf.seek(0)
            await channels.debug.send(
                f"`{self.ctx.message.content}` by {self.ctx.author.mention}: {self.ctx.message.jump_url}",
                file=discord.File(buf, filename="error.log"),
            )
            raise self.error
        else:
            setattr(self.error, "__handled__", True)

    def _get_err_embed(
        self, title: str, description: str | None, suggs: Suggestions | None = None, sugg_cmd_override: list[str] = []
    ) -> discord.Embed:
        emb = discord.Embed(title=title, description=description, colour=COLOUR_ERROR)
        if suggs is not None:
            if len(suggs) > 1:
                emb.add_field(name="Did you mean:", value="\n".join(f"- {desc}" for _k, desc in suggs), inline=False)
            if not sugg_cmd_override:
                v = self.ctx.view
                emb.add_field(
                    name="Suggested commands:",
                    value=(
                        "```php\n"
                        f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}\n"
                        f"{v.buffer[:v.previous]}{suggs[0][0]}{v.buffer[v.index:]}\n"
                        "```"
                    ),
                    inline=False,
                )
        if sugg_cmd_override:
            emb.add_field(
                name="Suggested Commands:",
                value="```php\n" + "\n".join(sugg_cmd_override) + "```",
            )
        return emb

    async def invalid_aircraft(self):
        if not isinstance(self.error, AircraftNotFoundError):
            return
        acsr = self.error.acsr
        suggs = Aircraft.suggest(acsr.parse_result)

        extra = f" using search mode `{st}`" if (st := acsr.parse_result.search_type) != Aircraft.SearchType.ALL else ""
        extra_mod = "You might also want to check the engine modifiers." if "[" in self.ctx.current_argument else ""
        embed = self._get_err_embed(
            title=f"Aircraft `{self.ctx.current_argument}` not found{extra}!",
            description=f"{self.err_tb}{extra_mod}",
            suggs=[(a.ac.shortname, f"`{a.ac.shortname}` ({a.ac.name})") for a in suggs],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_airport(self, *, route_typo: bool = False):
        if not isinstance(self.error, AirportNotFoundError):
            return
        apsr = self.error.apsr
        suggs = Airport.suggest(apsr.parse_result)

        extra = f" using search mode `{st}`" if (st := apsr.parse_result.search_type) != Airport.SearchType.ALL else ""
        typo_help = ""
        if route_typo:
            acsr = Aircraft.search(self.ctx.current_argument)
            if acsr.ac.valid:
                typo_help = f"`{self.ctx.current_argument}` is an aircraft. "
            typo_help += "You are currently using the `route` command. Maybe you meant to use the `routes` command?"
        embed = self._get_err_embed(
            title=f"Airport `{self.ctx.current_argument}` not found{extra}!",
            description=self.err_tb + typo_help,
            suggs=[(a.ap.iata.lower(), f"`{a.ap.iata}` / `{a.ap.icao}` ({a.ap.name}, {a.ap.country})") for a in suggs],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_setting_value(self):
        if not isinstance(self.error, SettingValueValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid setting value!",
            description=f"{self.err_tb}Details:\n{self.error.msg}".strip(),
            suggs=[("<value>", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_tpd(self):
        if not isinstance(self.error, TPDValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid trips per day!",
            description=f"{self.err_tb}Details:\n{self.error.msg}".strip(),
            suggs=[("3", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_cfg_alg(self):
        if not isinstance(self.error, CfgAlgValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid configuration algorithm!",
            description=f"{self.err_tb}\n{self.error.msg}".strip(),
            suggs=[("AUTO", "")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_constraint(self):
        if not isinstance(self.error, ConstraintValidationError):
            return
        as_time = self.error.err.errors()[0]["type"] == "time_delta_parsing"
        extra = (
            "**Tip**: I'm assuming the constraint is by time: correct it using `HH:MM`."
            if as_time
            else "**Tip**: I'm assuming the constraint is by distance: if you'd like to use time instead, use `HH:MM`."
        )
        embed = self._get_err_embed(
            title="Invalid constraint!",
            description=f"{self.err_tb}\n{self.error.msg}\n{extra}".strip(),
            suggs=[("08:00", "`08:00`")] if as_time else [("08:00", "`08:00`"), ("15000", "`15000`")],
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def invalid_price(self):
        if not isinstance(self.error, PriceValidationError):
            return
        embed = self._get_err_embed(
            title="Invalid price!",
            description=f"{self.err_tb}\n{self.error.msg}".strip(),
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def banned_user(self):
        if not isinstance(self.error, UserBannedError):
            return
        await self.ctx.send(
            embed=self._get_err_embed(
                title="You are not allowed to use this command.",
                description="If you think this is a mistake, contact a moderator.",
            )
        )
        self.handled = True

    async def too_many_args(self, arg_name: str):
        if not isinstance(self.error, commands.TooManyArguments):
            return
        v = self.ctx.view
        # override
        highlight = "▔" * len(v.buffer[v.index + 1 :])
        err_loc = f"```php\n{v.buffer}\n{' ' * (v.index+1)}{highlight}\n```"

        cmds = [f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}", f"{v.buffer[: v.index]}"]
        if a := self.ctx.current_argument:
            cmds.append(f'{v.buffer[: v.previous]}"{a}{v.buffer[v.index:]}"')

        await self.ctx.send(
            embed=self._get_err_embed(
                title="Too many arguments!",
                description=(
                    f"{err_loc}Tip: If you are trying to use spaces in the {arg_name},"
                    f' wrap it in double quotes (`"`).'
                ),
                sugg_cmd_override=cmds,
            )
        )
        self.handled = True

    async def bad_literal(self, get_cmd_suggs: Callable[[list[str]], list[str]]):
        if not isinstance(self.error, commands.BadLiteralArgument):
            return

        valid_literals = ", ".join(f"`{l}`" for l in self.error.literals)
        top_keys = []
        for k in self.error.literals:
            heapq.heappush(top_keys, (jaro_winkler_distance(self.error.argument, k), k))
        suggs = [k for _, k in heapq.nlargest(3, top_keys)]

        cp = self.ctx.current_parameter
        embed = self._get_err_embed(
            title=f"Provided argument `{self.ctx.current_argument}` is invalid.",
            description=f"{self.err_tb}Here, the `{cp.name}` must be one of: {valid_literals}.",
            suggs=[(s, s) for s in suggs],
            sugg_cmd_override=get_cmd_suggs(suggs),
        )
        await self.ctx.send(embed=embed)
        self.handled = True

    async def _missing_arg(self):
        if not isinstance(self.error, commands.MissingRequiredArgument):
            return
        pre = self.ctx.view.buffer[: self.ctx.view.previous]
        cp = self.ctx.current_parameter
        await self.ctx.send(
            embed=self._get_err_embed(
                title="Missing required argument!",
                description=(f"{self.err_tb}I expected the `{cp.name}` argument.\n"),
                sugg_cmd_override=[f"{cfg.bot.COMMAND_PREFIX}help {self.cmd}", f"{pre} <{cp.name}>"],
            )
        )
        self.handled = True

    async def _expected_closing_quote_error(self):
        if not isinstance(self.error, commands.ExpectedClosingQuoteError):
            return
        v = self.ctx.view
        await self.ctx.send(
            embed=self._get_err_embed(
                title="Missing closing quote!",
                description=f"{self.err_tb}You forgot to close the quote here.",
                sugg_cmd_override=[f'{v.buffer[:v.index]}"{v.buffer[v.index:]}'],
            )
        )
        self.handled = True

    async def _invalid_end_of_quoted_string_error(self):
        if not isinstance(self.error, commands.InvalidEndOfQuotedStringError):
            return
        v = self.ctx.view
        await self.ctx.send(
            embed=self._get_err_embed(
                title="Invalid end of quoted string!",
                description=f"{self.err_tb}You can't have anything after this closing quote.",
                sugg_cmd_override=[f"{v.buffer[:v.index]}"],
            )
        )
        self.handled = True

    async def _unexpected_quote_error(self):
        if not isinstance(self.error, commands.UnexpectedQuoteError):
            return
        v = self.ctx.view
        await self.ctx.send(
            embed=self._get_err_embed(
                title="Unexpected quote!",
                description=f"{self.err_tb}You can't have a quote after this character.",
                sugg_cmd_override=[f"{v.buffer[:v.index]}{v.buffer[v.index+1:]}"],
            )
        )
        self.handled = True

    async def _main_server_only(self):
        if not isinstance(self.error, OutsideMainServerError):
            return
        await self.ctx.send(
            embed=self._get_err_embed(
                title="This command can only be used on our official server!",
                description="Join our server [here](https://discord.gg/4tVQHtf).",
            )
        )
        self.handled = True

    async def _no_pm(self):
        if not isinstance(self.error, commands.NoPrivateMessage):
            return
        await self.ctx.send(
            embed=self._get_err_embed(
                title="This command cannot be used in private messages!",
                description="Join our server [here](https://discord.gg/4tVQHtf).",
            )
        )
        self.handled = True

    async def _command_not_found(self):
        if not isinstance(self.error, commands.CommandNotFound):
            return
        v = self.ctx.view
        command = v.buffer[v.previous : v.index]

        top_keys = []
        for c in self.ctx.bot.commands:
            heapq.heappush(top_keys, (jaro_winkler_distance(command, c.name), c.name))
        suggs = [k for _, k in heapq.nlargest(3, top_keys)]

        await self.ctx.send(
            embed=self._get_err_embed(
                title=f"`{command}` is not a valid command!",
                description=f"{self.err_tb}Check `{cfg.bot.COMMAND_PREFIX}help` to list all commands.",
                suggs=[("", f"`{cfg.bot.COMMAND_PREFIX}{s}`") for s in suggs],
                sugg_cmd_override=[f"{cfg.bot.COMMAND_PREFIX}help"],
            )
        )
        self.handled = True

    async def common_mistakes(self):
        await self._missing_arg()
        await self._expected_closing_quote_error()
        await self._invalid_end_of_quoted_string_error()
        await self._unexpected_quote_error()
        await self._main_server_only()

    async def top_level(self):
        await self._no_pm()
        await self._command_not_found()
