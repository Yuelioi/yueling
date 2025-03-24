from common.base.Plugin import load_mods

sub_plugins = load_mods(
  "funny",
  *["chat", "fortune", "hot", "poke", "repeater", "jm", "recorder", "sleep", "trace_moe"],
)
