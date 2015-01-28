<div class="listal-widget">
    <ul>
    % for item in items:
        <li><img src="{{item['image']}}"/> {{item['title']}}</li>
    % end
    </ul>
</div>
