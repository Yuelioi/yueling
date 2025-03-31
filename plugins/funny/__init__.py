from common.base.Plugin import load_mods

sub_plugins = load_mods(
  "funny",
  *["chat", "fortune", "hot", "poke", "repeater", "recorder", "jm", "sleep", "trace_moe"],
)
