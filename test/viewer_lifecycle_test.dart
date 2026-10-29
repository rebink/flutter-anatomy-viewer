import 'dart:convert';

import 'package:anatomy_viewer/main.dart';
import 'package:anatomy_viewer/anatomy_style.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:webview_flutter_platform_interface/webview_flutter_platform_interface.dart';

// Exercise the real Flutter screen without requiring a native WebView in widget tests.
class TestWebViewPlatform extends WebViewPlatform {
  late TestController controller;
  late TestNavigation navigation;
  @override
  PlatformWebViewController createPlatformWebViewController(
          PlatformWebViewControllerCreationParams params) =>
      controller = TestController(params);
  @override
  PlatformNavigationDelegate createPlatformNavigationDelegate(
          PlatformNavigationDelegateCreationParams params) =>
      navigation = TestNavigation(params);
  @override
  PlatformWebViewWidget createPlatformWebViewWidget(
          PlatformWebViewWidgetCreationParams params) =>
      TestViewer(params);
}

class TestController extends PlatformWebViewController {
  TestController(super.params) : super.implementation();
  final scripts = <String>[];
  late JavaScriptChannelParams channel;
  void message(String value) =>
      channel.onMessageReceived(JavaScriptMessage(message: value));
  @override
  Future<void> setJavaScriptMode(JavaScriptMode mode) async {}
  @override
  Future<void> setBackgroundColor(Color color) async {}
  @override
  Future<void> addJavaScriptChannel(JavaScriptChannelParams params) async {
    channel = params;
  }

  @override
  Future<void> setPlatformNavigationDelegate(
      PlatformNavigationDelegate handler) async {}
  @override
  Future<void> loadFlutterAsset(String key) async {}
  @override
  Future<void> runJavaScript(String script) async {
    scripts.add(script);
  }
}

class TestNavigation extends PlatformNavigationDelegate {
  TestNavigation(super.params) : super.implementation();
  late NavigationRequestCallback navigate;
  late PageEventCallback pageStarted;
  @override
  Future<void> setOnNavigationRequest(
      NavigationRequestCallback callback) async {
    navigate = callback;
  }

  @override
  Future<void> setOnPageStarted(PageEventCallback callback) async {
    pageStarted = callback;
  }

  @override
  Future<void> setOnWebResourceError(WebResourceErrorCallback callback) async {}
}

class TestViewer extends PlatformWebViewWidget {
  TestViewer(super.params) : super.implementation();
  @override
  Widget build(BuildContext context) => const SizedBox();
}

class MissingCreditsBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async =>
      throw FlutterError('Missing test asset: $key');
}

void main() {
  for (final entryUrl in [
    'file:///android_asset/flutter_assets/assets/viewer/index.html',
    'file:///private/app/Frameworks/App.framework/flutter_assets/assets/viewer/index.html',
  ]) {
    testWidgets('WebView restricts navigation to its bundled entry: $entryUrl',
        (tester) async {
      final oldPlatform = WebViewPlatform.instance;
      final platform = TestWebViewPlatform();
      WebViewPlatform.instance = platform;
      addTearDown(() {
        if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
      });
      await tester.pumpWidget(const AnatomyApp());
      final navigation = platform.navigation;
      Future<NavigationDecision> decision(String url,
              {bool isMainFrame = true}) async =>
          navigation
              .navigate(NavigationRequest(url: url, isMainFrame: isMainFrame));
      expect(await decision(entryUrl), NavigationDecision.navigate);
      navigation.pageStarted(entryUrl);
      expect(await decision(entryUrl), NavigationDecision.navigate);
      expect(await decision(entryUrl, isMainFrame: false),
          NavigationDecision.prevent);
      for (final url in [
        'https://example.com/',
        'javascript:alert(1)',
        'data:text/html,untrusted',
        'file:///private/untrusted.html',
        'file:///other/flutter_assets/assets/viewer/index.html',
        'file://remote/flutter_assets/assets/viewer/index.html',
        '$entryUrl?unexpected=true',
        '$entryUrl#unexpected',
      ]) {
        expect(await decision(url), NavigationDecision.prevent, reason: url);
      }
      await tester.pumpWidget(const SizedBox());
    });
  }

  testWidgets('Missing credits show a readable redistribution warning',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    WebViewPlatform.instance = TestWebViewPlatform();
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
    });
    await tester.pumpWidget(DefaultAssetBundle(
        bundle: MissingCreditsBundle(), child: const AnatomyApp()));
    await tester.tap(find.byTooltip('Credits and licenses'));
    await tester.pumpAndSettle();
    expect(find.text('Anatomy credits'), findsOneWidget);
    expect(find.textContaining('Required anatomy credits could not be loaded.'),
        findsOneWidget);
    expect(find.textContaining('Do not redistribute'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('Viewer status and controls fit at enlarged text sizes',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    final platform = TestWebViewPlatform();
    WebViewPlatform.instance = platform;
    tester.view.physicalSize = const Size(320, 844);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 3;
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
      tester.platformDispatcher.clearTextScaleFactorTestValue();
    });
    await tester.pumpWidget(const AnatomyApp());
    platform.controller.message('{"type":"ready"}');
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
    for (final mode in ['Muscles', 'Bones', 'Body Parts']) {
      await tester.scrollUntilVisible(find.text(mode), 200);
      await Scrollable.ensureVisible(tester.element(find.text(mode)),
          alignment: 0.5);
      await tester.pumpAndSettle();
      await tester.tap(find.text(mode));
      await tester.pumpAndSettle();
      final status = find.descendant(
          of: find.byWidgetPredicate((widget) =>
              widget is Semantics && widget.properties.liveRegion == true),
          matching: find.byType(Text));
      expect(
          tester.widget<Text>(status).data,
          switch (mode) {
            'Muscles' => '28 major muscles · tap to highlight',
            'Bones' => '33 bones / groups · tap to highlight',
            _ => '2 example findings · lungs',
          });
      final statusRect = tester.getRect(status);
      expect(statusRect.left, greaterThanOrEqualTo(0));
      expect(statusRect.right, lessThanOrEqualTo(320));
      expect(find.text('DRAG TO ROTATE  ·  PINCH TO ZOOM'), findsNothing);
      final resetRect = tester.getRect(find.byTooltip('Reset body view'));
      expect(statusRect.bottom, lessThanOrEqualTo(resetRect.top));
      expect(tester.takeException(), isNull);
    }
    await tester.scrollUntilVisible(find.text('Report overview'), 200);
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('Credits stay readable after viewer failure with enlarged text',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    final platform = TestWebViewPlatform();
    WebViewPlatform.instance = platform;
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
      tester.platformDispatcher.clearTextScaleFactorTestValue();
    });
    await tester.pumpWidget(const AnatomyApp());
    await tester.pump(const Duration(seconds: 2));
    platform.controller.message('{"type":"error"}');
    await tester.pumpAndSettle();
    expect(find.text('3D unavailable. Findings remain accessible below.'),
        findsOneWidget);
    await tester.tap(find.byTooltip('Credits and licenses'));
    await tester.pumpAndSettle();
    expect(find.text('Anatomy credits'), findsOneWidget);
    expect(find.textContaining('BodyParts3D'), findsOneWidget);
    expect(find.textContaining('CC BY-SA 2.1 Japan'), findsOneWidget);
    expect(
        find.textContaining(
            'https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode'),
        findsOneWidget);
    expect(find.textContaining('Modifications for this prototype'),
        findsOneWidget);
    final scrollable = find.descendant(
        of: find.byType(AlertDialog), matching: find.byType(Scrollable));
    final scrollState = tester.state<ScrollableState>(scrollable);
    expect(scrollState.position.maxScrollExtent, greaterThan(0));
    await tester.drag(scrollable, const Offset(0, -350));
    await tester.pumpAndSettle();
    expect(scrollState.position.pixels, greaterThan(0));
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    expect(find.text('Anatomy credits'), findsNothing);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('Muscle and bone modes select, isolate and survive viewer reload',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    final platform = TestWebViewPlatform();
    WebViewPlatform.instance = platform;
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
    });
    await tester.pumpWidget(const AnatomyApp());
    final controller = platform.controller;
    controller.message('{"type":"ready"}');
    await tester.tap(find.text('Muscles'));
    await tester.pumpAndSettle();
    Map<String, dynamic> lastConfig() {
      final script = controller.scripts
          .lastWhere((s) => s.startsWith('window.anatomy.configure('));
      return jsonDecode(script.substring(
              'window.anatomy.configure('.length, script.length - 2))
          as Map<String, dynamic>;
    }

    expect(lastConfig()['mode'], 'muscles');
    expect(lastConfig()['loading'], false);
    expect(lastConfig()['findings'], isEmpty);
    expect(find.byTooltip('Credits and licenses'), findsOneWidget);
    controller.message('{"type":"select","value":"lung_left"}');
    await tester.pumpAndSettle();
    expect(find.text('Not assessed'), findsNothing);
    controller.message('{"type":"select","value":"muscle_deltoid_left"}');
    await tester.pumpAndSettle();
    expect(find.text('Selected muscle'), findsOneWidget);
    expect(controller.scripts,
        contains('window.anatomy.focus("muscle_deltoid_left");'));
    Navigator.of(tester.element(find.text('Selected muscle'))).pop();
    await tester.pumpAndSettle();
    controller.message('{"type":"ready"}');
    expect(lastConfig()['mode'], 'muscles');
    await tester.tap(find.text('Bones'));
    await tester.pumpAndSettle();
    expect(lastConfig()['mode'], 'bones');
    expect(lastConfig()['loading'], false);
    expect(lastConfig()['findings'], isEmpty);
    expect(find.byTooltip('Credits and licenses'), findsOneWidget);
    controller.message('{"type":"select","value":"lung_left"}');
    controller.message('{"type":"select","value":"muscle_deltoid_left"}');
    await tester.pumpAndSettle();
    expect(find.text('Selected muscle'), findsNothing);
    expect(find.text('Not assessed'), findsNothing);
    controller.message('{"type":"select","value":"bone_femur_left"}');
    await tester.pumpAndSettle();
    expect(find.text('Selected bone'), findsOneWidget);
    expect(controller.scripts,
        contains('window.anatomy.focus("bone_femur_left");'));
    Navigator.of(tester.element(find.text('Selected bone'))).pop();
    await tester.pumpAndSettle();
    controller.message('{"type":"ready"}');
    expect(lastConfig()['mode'], 'bones');
    await tester.tap(find.text('Muscles'));
    await tester.pumpAndSettle();
    controller.message('{"type":"select","value":"bone_femur_left"}');
    await tester.pumpAndSettle();
    expect(find.text('Selected bone'), findsNothing);
    await tester.tap(find.text('Body Parts'));
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
    expect(lastConfig()['mode'], 'body');
    expect(lastConfig()['findings']['lung_left'], 'danger');
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets(
      'Custom light theme and organ colors reach UI and viewer on updates',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    final platform = TestWebViewPlatform();
    WebViewPlatform.instance = platform;
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
    });
    const danger = Color(0xFFB42318);
    const style = AnatomyStyle(
      bodyShell: Color(0xFF235678),
      danger: danger,
      warning: Color(0xFF9C5D00),
      organColors: {'brain': Color(0xFF123456)},
    );
    final light = ThemeData.light()
        .copyWith(scaffoldBackgroundColor: const Color(0xFFF4F1EA));
    await tester.pumpWidget(AnatomyApp(theme: light, style: style));
    final controller = platform.controller;
    controller.message('{"type":"ready"}');
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
    Map<String, dynamic> lastConfig() {
      final script = controller.scripts
          .lastWhere((s) => s.startsWith('window.anatomy.configure('));
      return jsonDecode(script.substring(
              'window.anatomy.configure('.length, script.length - 2))
          as Map<String, dynamic>;
    }

    expect(lastConfig()['style']['background'], '#f4f1ea');
    expect(lastConfig()['style']['danger'], '#b42318');
    expect(lastConfig()['style']['organColors'], {'brain': '#123456'});
    final label = tester.widget<Text>(find.text('Danger · DEMO').first);
    expect(label.style?.color, danger);
    expect(Theme.of(tester.element(find.byType(AnatomyScreen))).brightness,
        Brightness.light);
    // Rebuild the same screen, preserving WebView state and applying a new palette.
    await tester.pumpWidget(AnatomyApp(
        theme: ThemeData.dark(),
        style: const AnatomyStyle(danger: Color(0xFFAA2277))));
    await tester.pumpAndSettle();
    expect(identical(controller, platform.controller), isTrue);
    expect(lastConfig()['style']['danger'], '#aa2277');
    expect(lastConfig()['style']['organColors']['brain'], '#b9dfd5');
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('Readiness and app resume preserve details-route pause state',
      (tester) async {
    final oldPlatform = WebViewPlatform.instance;
    final platform = TestWebViewPlatform();
    WebViewPlatform.instance = platform;
    addTearDown(() {
      if (oldPlatform != null) WebViewPlatform.instance = oldPlatform;
    });
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    await tester.pumpWidget(const AnatomyApp());
    final controller = platform.controller;
    // Becoming ready in the background must not start drawing.
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
    controller.message('{"type":"ready"}');
    await tester.pump();
    expect(controller.scripts.last, 'window.anatomy.pause(true);');
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    expect(controller.scripts.last, 'window.anatomy.pause(false);');
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
    controller.message('{"type":"select","value":"lung_left"}');
    await tester.pumpAndSettle();
    await tester.tap(find.text('View details'));
    await tester.pumpAndSettle();
    expect(find.text('Finding details'), findsOneWidget);
    expect(controller.scripts.last, 'window.anatomy.pause(true);');
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    expect(controller.scripts.last, 'window.anatomy.pause(true);');
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(controller.scripts.last, 'window.anatomy.pause(false);');
    expect(find.byTooltip('Rotate left'), findsOneWidget);
    expect(find.byTooltip('Zoom in'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });
}
