import 'dart:ui' show ColorSpace;

import 'package:flutter/material.dart';

/// Appearance only: colors never determine clinical severity or organ identity.
@immutable
class AnatomyStyle {
  const AnatomyStyle({
    this.bodyShell = const Color(0xFF75CEDB),
    this.neutralOrgan = const Color(0xFF80C6D0),
    this.warning = const Color(0xFFFFBD68),
    this.danger = const Color(0xFFFF6E73),
    this.organColors = defaultOrganColors,
    this.backgroundHighlight,
    this.keyLight = const Color(0xFFD5F6FF),
    this.rimLight = const Color(0xFF41BBB7),
    this.ambientSky = const Color(0xFFC5FFFF),
    this.ambientGround = const Color(0xFF143240),
  });

  final Color bodyShell, neutralOrgan, warning, danger;

  /// RGB surface colors. Use the viewer's opacity control for transparency.
  /// Missing organs use [neutralOrgan]. Pass an empty map for a uniform palette.
  final Map<String, Color> organColors;
  final Color? backgroundHighlight;
  final Color keyLight, rimLight, ambientSky, ambientGround;

  static const defaultOrganColors = <String, Color>{
    'brain': Color(0xFFB9DFD5),
    'airway': Color(0xFF89DCF1),
    'esophagus': Color(0xFF759BD5),
    'lung_left': Color(0xFF60D7C2),
    'lung_right': Color(0xFF60D7C2),
    'heart': Color(0xFF9EBCFA),
    'liver': Color(0xFF548FB5),
    'stomach': Color(0xFFA4E4BE),
    'small_intestine': Color(0xFF66CBA1),
    'large_intestine': Color(0xFFB0E1CD),
    'kidney_left': Color(0xFF8CAEDF),
    'kidney_right': Color(0xFF8CAEDF),
    'bladder': Color(0xFF98D5EA),
    'pancreas': Color(0xFFC4D9C8),
    'gallbladder': Color(0xFF76C9BB),
  };

  Color severityColor(String severity) => switch (severity) {
        'warning' => warning,
        'danger' => danger,
        _ => neutralOrgan,
      };

  Map<String, Object> toViewer(ThemeData theme) {
    String rgb(Color color) {
      final srgb = color.withValues(colorSpace: ColorSpace.sRGB);
      return '#${[
        srgb.r,
        srgb.g,
        srgb.b
      ].map((value) => (value.clamp(0.0, 1.0) * 255).round().toRadixString(16).padLeft(2, '0')).join()}';
    }

    return {
      'bodyShell': rgb(bodyShell),
      'neutralOrgan': rgb(neutralOrgan),
      'warning': rgb(warning),
      'danger': rgb(danger),
      'organColors': organColors.map((id, color) => MapEntry(id, rgb(color))),
      'background': rgb(theme.scaffoldBackgroundColor),
      'backgroundHighlight':
          rgb(backgroundHighlight ?? theme.colorScheme.surfaceContainerHighest),
      'foreground': rgb(theme.colorScheme.onSurface),
      'keyLight': rgb(keyLight),
      'rimLight': rgb(rimLight),
      'ambientSky': rgb(ambientSky),
      'ambientGround': rgb(ambientGround),
    };
  }
}
