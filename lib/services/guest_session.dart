import 'package:flutter/foundation.dart';

class GuestSession {
  GuestSession._();

  static final ValueNotifier<bool> active = ValueNotifier<bool>(false);

  static bool get isGuest => active.value;

  static void enter() => active.value = true;

  static void exit() => active.value = false;
}
